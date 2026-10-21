// Vertical sizzle cutter: EDL JSON -> graded, silent H.264 MP4 (+ optional stills).
// usage: cut <edl.json> <width> <height> <bitrate> <out.mp4> [stillsDir]
import Foundation
import AVFoundation
import CoreImage
import ImageIO
import UniformTypeIdentifiers

struct Shot: Codable {
  let file: String; let start: Double; let frames: Int
  var fx: Double? = nil; var fy: Double? = nil
  var z0: Double? = nil; var z1: Double? = nil; var punch: Bool? = nil
  var ev: Double? = nil; var speed: Double? = nil; var sat: Double? = nil
  var still: Bool? = nil
}
struct EDL: Codable { let fps: Int; let shots: [Shot] }

let a = CommandLine.arguments
let edl = try! JSONDecoder().decode(EDL.self, from: Data(contentsOf: URL(fileURLWithPath: a[1])))
let OW = Int(a[2])!, OH = Int(a[3])!, bitrate = Int(a[4])!
let outURL = URL(fileURLWithPath: a[5])
let stillsDir: URL? = a.count > 6 ? URL(fileURLWithPath: a[6]) : nil
let fps = Double(edl.fps)

// ---------- the grade: one 3D LUT, petrol shadows, amber highlights ----------
func makeLUT(_ n: Int) -> Data {
  var cube = [Float](repeating: 0, count: n * n * n * 4)
  func sig(_ x: Double, _ k: Double) -> Double { 1 / (1 + exp(-k * (x - 0.5))) }
  let s0 = sig(0, 4.6), s1 = sig(1, 4.6)
  for bi in 0..<n { for gi in 0..<n { for ri in 0..<n {
    var r = Double(ri) / Double(n - 1), g = Double(gi) / Double(n - 1), b = Double(bi) / Double(n - 1)
    // hue work in HSV: pull violet/blue screens toward teal, greens toward teal
    let mx = max(r, g, b), mn = min(r, g, b), d = mx - mn
    var h = 0.0
    if d > 1e-6 {
      if mx == r { h = 60 * ((g - b) / d).truncatingRemainder(dividingBy: 6) }
      else if mx == g { h = 60 * ((b - r) / d + 2) } else { h = 60 * ((r - g) / d + 4) }
      if h < 0 { h += 360 }
    }
    var sv = mx > 0 ? d / mx : 0, v = mx
    if h > 200 && h < 300 { let w = 1 - abs(h - 245) / 55; h -= 32 * max(0, w); sv *= 1 - 0.22 * max(0, w) }
    if h > 75 && h < 165 { let w = 1 - abs(h - 120) / 45; h += 26 * max(0, w); sv *= 1 - 0.18 * max(0, w) }
    // back to rgb
    let c = v * sv, hp = h / 60, x = c * (1 - abs(hp.truncatingRemainder(dividingBy: 2) - 1)), m = v - c
    var (rr, gg, bb) = (0.0, 0.0, 0.0)
    switch Int(hp) { case 0: (rr, gg, bb) = (c, x, 0); case 1: (rr, gg, bb) = (x, c, 0); case 2: (rr, gg, bb) = (0, c, x)
      case 3: (rr, gg, bb) = (0, x, c); case 4: (rr, gg, bb) = (x, 0, c); default: (rr, gg, bb) = (c, 0, x) }
    r = rr + m; g = gg + m; b = bb + m
    // filmic contrast, lifted toe
    func tone(_ x: Double) -> Double { 0.028 + 0.95 * (sig(pow(max(0, x), 1.03), 4.6) - s0) / (s1 - s0) }
    r = tone(r); g = tone(g); b = tone(b)
    let y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    // global saturation trim
    r = y + (r - y) * 0.9; g = y + (g - y) * 0.9; b = y + (b - y) * 0.9
    // split tone
    let ws = pow(1 - y, 1.6), wh = pow(y, 1.7)
    r += -0.040 * ws + 0.052 * wh
    g +=  0.022 * ws + 0.018 * wh
    b +=  0.036 * ws - 0.046 * wh
    let i = ((bi * n + gi) * n + ri) * 4
    cube[i] = Float(min(1, max(0, r))); cube[i + 1] = Float(min(1, max(0, g))); cube[i + 2] = Float(min(1, max(0, b))); cube[i + 3] = 1
  } } }
  return cube.withUnsafeBufferPointer { Data(buffer: $0) }
}
let LUTN = 33
let lutData = makeLUT(LUTN)
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!
let ctx = CIContext(options: [.workingColorSpace: CGColorSpace(name: CGColorSpace.extendedLinearSRGB)!, .outputColorSpace: CGColorSpace(name: CGColorSpace.itur_709)!])

func grade(_ img: CIImage, sat: Double) -> CIImage {
  var im = img
  if sat != 1 { im = im.applyingFilter("CIColorControls", parameters: ["inputSaturation": sat, "inputContrast": 1.0, "inputBrightness": 0]) }
  im = im.applyingFilter("CIColorCubeWithColorSpace", parameters: ["inputCubeDimension": LUTN, "inputCubeData": lutData, "inputColorSpace": srgb])
  im = im.applyingFilter("CIVignette", parameters: ["inputIntensity": 0.55, "inputRadius": 1.6])
  return im
}

// ---------- writer ----------
try? FileManager.default.removeItem(at: outURL)
let writer = try! AVAssetWriter(outputURL: outURL, fileType: .mp4)
writer.shouldOptimizeForNetworkUse = true
let color: [String: Any] = [AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2, AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2, AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2]
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
  AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: OW, AVVideoHeightKey: OH, AVVideoColorPropertiesKey: color,
  AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: bitrate, AVVideoMaxKeyFrameIntervalKey: 60,
    AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel, AVVideoH264EntropyModeKey: AVVideoH264EntropyModeCABAC,
    AVVideoExpectedSourceFrameRateKey: edl.fps, AVVideoAllowFrameReorderingKey: true]
])
input.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
  kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA, kCVPixelBufferWidthKey as String: OW, kCVPixelBufferHeightKey as String: OH,
  kCVPixelBufferIOSurfacePropertiesKey as String: [:]])
writer.add(input)
writer.startWriting(); writer.startSession(atSourceTime: .zero)

func saveJPEG(_ img: CIImage, _ url: URL) {
  guard let cg = ctx.createCGImage(img, from: CGRect(x: 0, y: 0, width: OW, height: OH), format: .RGBA8, colorSpace: srgb) else { return }
  let dest = CGImageDestinationCreateWithURL(url as CFURL, UTType.jpeg.identifier as CFString, 1, nil)!
  CGImageDestinationAddImage(dest, cg, [kCGImageDestinationLossyCompressionQuality: 0.86] as CFDictionary)
  CGImageDestinationFinalize(dest)
}

var outFrame: Int64 = 0
for (si, shot) in edl.shots.enumerated() {
  let asset = AVURLAsset(url: URL(fileURLWithPath: (shot.file as NSString).expandingTildeInPath))
  let vt = try! await asset.loadTracks(withMediaType: .video).first!
  let comp = try! await AVMutableVideoComposition.videoComposition(withPropertiesOf: asset)
  comp.colorPrimaries = AVVideoColorPrimaries_ITU_R_709_2
  comp.colorTransferFunction = AVVideoTransferFunction_ITU_R_709_2
  comp.colorYCbCrMatrix = AVVideoYCbCrMatrix_ITU_R_709_2
  let speed = shot.speed ?? 1
  let reader = try! AVAssetReader(asset: asset)
  reader.timeRange = CMTimeRange(start: CMTime(seconds: shot.start, preferredTimescale: 6000),
                                 duration: CMTime(seconds: Double(shot.frames) / fps * speed + 0.25, preferredTimescale: 6000))
  let out = AVAssetReaderVideoCompositionOutput(videoTracks: [vt], videoSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
  out.videoComposition = comp
  out.alwaysCopiesSampleData = false
  reader.add(out)
  guard reader.startReading() else { print("READER FAIL", shot.file, reader.error as Any); exit(1) }
  var cur: CMSampleBuffer? = nil, nxt: CMSampleBuffer? = out.copyNextSampleBuffer()
  for j in 0..<shot.frames {
    let need = shot.start + Double(j) / fps * speed
    while let n = nxt, CMSampleBufferGetPresentationTimeStamp(n).seconds <= need + 0.5 / fps / max(speed, 0.0001) * speed {
      cur = n; nxt = out.copyNextSampleBuffer()
    }
    if cur == nil { cur = nxt; nxt = out.copyNextSampleBuffer() }
    guard let sb = cur, let pb = CMSampleBufferGetImageBuffer(sb) else { print("NO FRAME", shot.file, j); break }
    var img = CIImage(cvPixelBuffer: pb)
    let W = img.extent.width, H = img.extent.height
    if let ev = shot.ev, ev != 0 { img = img.applyingFilter("CIExposureAdjust", parameters: ["inputEV": ev]) }
    // zoom: optional punch (1.14 -> base over 5 frames), else linear z0 -> z1
    let t = shot.frames > 1 ? Double(j) / Double(shot.frames - 1) : 0
    let zb0 = shot.z0 ?? 1, zb1 = shot.z1 ?? zb0
    var z = zb0 + (zb1 - zb0) * t
    if shot.punch == true { let k = min(1, Double(j) / 5); z *= 1 + 0.14 * pow(1 - k, 2) }
    let aspect = Double(OW) / Double(OH)
    var cw0 = Double(W), ch0 = Double(W) / aspect
    if Double(W) / Double(H) > aspect { ch0 = Double(H); cw0 = Double(H) * aspect }
    let cw = cw0 / z, ch = ch0 / z
    let cx = min(max((shot.fx ?? 0.5) * Double(W), cw / 2), Double(W) - cw / 2)
    let cyTop = (shot.fy ?? 0.5) * Double(H)
    let cy = min(max(Double(H) - cyTop, ch / 2), Double(H) - ch / 2)
    let s = Double(OW) / cw
    img = img.clampedToExtent()
      .transformed(by: CGAffineTransform(translationX: -(cx - cw / 2), y: -(cy - ch / 2)))
      .applyingFilter("CILanczosScaleTransform", parameters: ["inputScale": s, "inputAspectRatio": 1.0])
      .cropped(to: CGRect(x: 0, y: 0, width: OW, height: OH))
    img = grade(img, sat: shot.sat ?? 1)
    while !input.isReadyForMoreMediaData { usleep(1000) }
    var opb: CVPixelBuffer? = nil
    CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &opb)
    guard let o = opb else { print("POOL FAIL"); exit(1) }
    CVBufferSetAttachment(o, kCVImageBufferColorPrimariesKey, kCVImageBufferColorPrimaries_ITU_R_709_2, .shouldPropagate)
    CVBufferSetAttachment(o, kCVImageBufferTransferFunctionKey, kCVImageBufferTransferFunction_ITU_R_709_2, .shouldPropagate)
    CVBufferSetAttachment(o, kCVImageBufferYCbCrMatrixKey, kCVImageBufferYCbCrMatrix_ITU_R_709_2, .shouldPropagate)
    ctx.render(img, to: o, bounds: CGRect(x: 0, y: 0, width: OW, height: OH), colorSpace: CGColorSpace(name: CGColorSpace.itur_709)!)
    if !adaptor.append(o, withPresentationTime: CMTime(value: outFrame, timescale: CMTimeScale(edl.fps))) { print("APPEND FAIL", writer.error as Any); exit(1) }
    if let dir = stillsDir, (shot.still ?? true), j == shot.frames / 2 {
      saveJPEG(img, dir.appendingPathComponent(String(format: "s%02d.jpg", si)))
    }
    if let dir = stillsDir, si == 0, j == 0 { saveJPEG(img, dir.appendingPathComponent("poster.jpg")) }
    outFrame += 1
  }
  reader.cancelReading()
  print(String(format: "shot %02d  %3d f  %@", si, shot.frames, (shot.file as NSString).lastPathComponent))
}
input.markAsFinished()
await writer.finishWriting()
print("DONE", outFrame, "frames", String(format: "%.2fs", Double(outFrame) / fps), writer.status.rawValue, writer.error as Any)
