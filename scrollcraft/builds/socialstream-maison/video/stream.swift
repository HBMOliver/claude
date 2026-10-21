// The stream film: vertical cards flow like a feed being scrolled; the feed
// stops, one card blooms to full frame and plays, then folds back into the
// stream. Silent H.264, deterministic, one warm "cream film" grade.
// usage: stream <film.json> <W> <H> <bitrate> <out.mp4> [bg r,g,b] [stillsDir]
import Foundation
import AVFoundation
import CoreImage
import ImageIO
import UniformTypeIdentifiers

struct ClipRef: Codable { let file: String; let start: Double; var fx: Double? = nil; var fy: Double? = nil; var ev: Double? = nil }
struct Beat: Codable { let stop: Double; let hold: Double; let clip: ClipRef }
struct Film: Codable { let fps: Int; let duration: Double; let cards: [ClipRef]; let beats: [Beat]; var cols: Int? = nil }

setvbuf(stdout, nil, _IONBF, 0)
let a = CommandLine.arguments
let film = try! JSONDecoder().decode(Film.self, from: Data(contentsOf: URL(fileURLWithPath: (a[1] as NSString).expandingTildeInPath)))
let W = Double(a[2])!, H = Double(a[3])!, bitrate = Int(a[4])!
let outURL = URL(fileURLWithPath: a[5])
let bgc = (a.count > 6 ? a[6] : "0.937,0.914,0.874").split(separator: ",").map { Double($0)! }
let stillsDir: URL? = a.count > 7 ? URL(fileURLWithPath: a[7]) : nil
let fps = Double(film.fps)
let portrait = H > W

// ---------- layout ----------
let cols = film.cols ?? (portrait ? 2 : 5)
let gapX = portrait ? W * 0.045 : W * 0.022
let cardW = portrait ? (W - gapX * 3) / 2 : (W - gapX * Double(cols + 1)) / Double(cols)
let cardH = cardW * 16 / 9
let gapY = gapX
let pitch = cardH + gapY
let colX = (0..<cols).map { gapX + Double($0) * (cardW + gapX) }
let colSpeed: [Double] = portrait ? [1.0, 0.82] : [0.86, 1.0, 0.92, 1.06, 0.8]
let colPhase: [Double] = portrait ? [0.0, 0.5] : [0.15, 0.62, 0.33, 0.8, 0.05]
let mid = cols / 2
let vmax = H * 1.05   // px per second at full scroll

// ---------- the grade: warm, soft, filmic ----------
func makeLUT(_ n: Int) -> Data {
  var cube = [Float](repeating: 0, count: n * n * n * 4)
  func sig(_ x: Double, _ k: Double) -> Double { 1 / (1 + exp(-k * (x - 0.5))) }
  let s0 = sig(0, 4.2), s1 = sig(1, 4.2)
  for bi in 0..<n { for gi in 0..<n { for ri in 0..<n {
    var r = Double(ri) / Double(n - 1), g = Double(gi) / Double(n - 1), b = Double(bi) / Double(n - 1)
    func tone(_ x: Double) -> Double { 0.045 + 0.925 * (sig(pow(max(0, x), 1.04), 4.2) - s0) / (s1 - s0) }
    r = tone(r); g = tone(g); b = tone(b)
    let y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    r = y + (r - y) * 0.8; g = y + (g - y) * 0.8; b = y + (b - y) * 0.8
    let ws = pow(1 - y, 1.8), wh = pow(y, 1.6)
    r += 0.022 * ws + 0.030 * wh
    g += 0.012 * ws + 0.016 * wh
    b += -0.004 * ws - 0.026 * wh
    let i = ((bi * n + gi) * n + ri) * 4
    cube[i] = Float(min(1, max(0, r))); cube[i + 1] = Float(min(1, max(0, g))); cube[i + 2] = Float(min(1, max(0, b))); cube[i + 3] = 1
  } } }
  return cube.withUnsafeBufferPointer { Data(buffer: $0) }
}
let LUTN = 33, lut = makeLUT(LUTN)
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!
let c709 = CGColorSpace(name: CGColorSpace.itur_709)!
let ctx = CIContext(options: [.workingColorSpace: CGColorSpace(name: CGColorSpace.extendedLinearSRGB)!, .outputColorSpace: c709, .cacheIntermediates: false])
func grade(_ i: CIImage) -> CIImage { i.applyingFilter("CIColorCubeWithColorSpace", parameters: ["inputCubeDimension": LUTN, "inputCubeData": lut, "inputColorSpace": srgb]) }

// ---------- readers ----------
func reader(_ c: ClipRef, _ seconds: Double) async -> (AVAssetReader, AVAssetReaderVideoCompositionOutput) {
  let asset = AVURLAsset(url: URL(fileURLWithPath: (c.file as NSString).expandingTildeInPath))
  let vt = try! await asset.loadTracks(withMediaType: .video).first!
  let comp = try! await AVMutableVideoComposition.videoComposition(withPropertiesOf: asset)
  comp.colorPrimaries = AVVideoColorPrimaries_ITU_R_709_2; comp.colorTransferFunction = AVVideoTransferFunction_ITU_R_709_2; comp.colorYCbCrMatrix = AVVideoYCbCrMatrix_ITU_R_709_2
  let total = try! await asset.load(.duration).seconds
  let st = min(c.start, max(0, total - 0.3))
  let r = try! AVAssetReader(asset: asset)
  r.timeRange = CMTimeRange(start: CMTime(seconds: st, preferredTimescale: 6000), duration: CMTime(seconds: max(0.2, min(seconds, total - st - 0.02)), preferredTimescale: 6000))
  let o = AVAssetReaderVideoCompositionOutput(videoTracks: [vt], videoSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
  o.videoComposition = comp; o.alwaysCopiesSampleData = false
  r.add(o); r.startReading()
  return (r, o)
}
// crop a source frame to an aspect around a focus, scale to w x h
func fit(_ src: CIImage, _ w: Double, _ h: Double, _ fx: Double, _ fy: Double) -> CIImage {
  let iw = src.extent.width, ih = src.extent.height, asp = w / h
  var cw = Double(iw), ch = Double(iw) / asp
  if Double(iw) / Double(ih) > asp { ch = Double(ih); cw = Double(ih) * asp }
  let cx = min(max(fx * Double(iw), cw / 2), Double(iw) - cw / 2)
  let cy = min(max(Double(ih) - fy * Double(ih), ch / 2), Double(ih) - ch / 2)
  return src.clampedToExtent()
    .transformed(by: CGAffineTransform(translationX: -(cx - cw / 2), y: -(cy - ch / 2)))
    .applyingFilter("CILanczosScaleTransform", parameters: ["inputScale": w / cw, "inputAspectRatio": 1.0])
    .cropped(to: CGRect(x: 0, y: 0, width: w, height: h))
}

// card thumbnails: 24 frames over 1.6 s, graded, rasterised once
let thumbN = 24, thumbStep = 2
var thumbs: [[CGImage]] = []
func loadThumbs(_ c: ClipRef) async -> [CGImage] {
  let (r, o) = await reader(c, Double(thumbN * thumbStep) / 30 + 0.4)
  var out: [CGImage] = [], k = 0
  while let sb = o.copyNextSampleBuffer() {
    if k % thumbStep == 0, let pb = CMSampleBufferGetImageBuffer(sb) {
      var im = CIImage(cvPixelBuffer: pb)
      if let ev = c.ev { im = im.applyingFilter("CIExposureAdjust", parameters: ["inputEV": ev]) }
      im = grade(fit(im, cardW.rounded(), cardH.rounded(), c.fx ?? 0.5, c.fy ?? 0.45))
      if let cg = ctx.createCGImage(im, from: CGRect(x: 0, y: 0, width: cardW.rounded(), height: cardH.rounded()), format: .RGBA8, colorSpace: srgb) { out.append(cg) }
      if out.count == thumbN { break }
    }
    k += 1
  }
  r.cancelReading()
  return out
}
let pool = film.cards + film.beats.map { $0.clip }
for c in pool { thumbs.append(await loadThumbs(c)) }
print("thumbs", thumbs.map { $0.count })

// ---------- timeline ----------
// speed(t) in px/s: full scroll, easing to a stop before each beat, held while the
// card is open, easing back after. open = 0.5 s, close = 0.5 s.
let openD = 0.5, closeD = 0.5, decel = 0.7, accel = 0.6
func spd(_ t: Double) -> Double {
  var v = 1.0
  for b in film.beats {
    let s0 = b.stop - decel, s1 = b.stop, e0 = b.stop + openD + b.hold + closeD, e1 = e0 + accel
    if t >= s0 && t < s1 { let k = (t - s0) / decel; v = min(v, 1 - k * k * (3 - 2 * k)) }
    if t >= s1 && t < e0 { v = 0 }
    if t >= e0 && t < e1 { let k = (t - e0) / accel; v = min(v, k * k * (3 - 2 * k)) }
  }
  return v * vmax
}
// integrate offset at frame resolution (deterministic)
let N = Int(film.duration * fps)
var off = [Double](repeating: 0, count: N + 1)
for i in 1...N { let t = Double(i - 1) / fps; off[i] = off[i - 1] + spd(t + 0.5 / fps) / fps }
func offsetAt(_ i: Int) -> Double { off[max(0, min(N, i))] }
// card k of column c sits at y = k*pitch - offset*speed + phase*pitch (moving up)
func cardY(_ c: Int, _ k: Int, _ i: Int) -> Double { Double(k) * pitch - offsetAt(i) * colSpeed[c] + colPhase[c] * pitch }
// which card is nearest centre in the middle column when a beat stops
var override: [String: Int] = [:]
var chosen: [Int] = []
for (bi, b) in film.beats.enumerated() {
  let i = Int(b.stop * fps)
  var best = 0, bd = 1e9
  for k in -3...400 { let y = cardY(mid, k, i) + cardH / 2; let d = abs(y - H / 2); if d < bd { bd = d; best = k } }
  override["\(mid):\(best)"] = film.cards.count + bi
  chosen.append(best)
}
func contentIndex(_ c: Int, _ k: Int) -> Int {
  if let o = override["\(c):\(k)"] { return o }
  let n = film.cards.count
  return ((k * 7 + c * 11) % n + n) % n
}

// ---------- shapes ----------
func roundRect(_ w: Double, _ h: Double, _ r: Double) -> CIImage {
  CIFilter(name: "CIRoundedRectangleGenerator", parameters: ["inputExtent": CIVector(x: 0, y: 0, z: w, w: h), "inputRadius": r, "inputColor": CIColor.white])!.outputImage!
}
let radius = cardW * 0.035
let cardMask = roundRect(cardW.rounded(), cardH.rounded(), radius)
let shadow = roundRect(cardW.rounded(), cardH.rounded(), radius)
  .applyingFilter("CIColorMatrix", parameters: ["inputRVector": CIVector(x: 0, y: 0, z: 0, w: 0), "inputGVector": CIVector(x: 0, y: 0, z: 0, w: 0), "inputBVector": CIVector(x: 0, y: 0, z: 0, w: 0), "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 0.26)])
  .clampedToExtent().cropped(to: CGRect(x: -60, y: -60, width: cardW + 120, height: cardH + 120))
  .applyingFilter("CIGaussianBlur", parameters: ["inputRadius": cardW * 0.06])
  .cropped(to: CGRect(x: -80, y: -80, width: cardW + 160, height: cardH + 160))
let bg = CIImage(color: CIColor(red: bgc[0], green: bgc[1], blue: bgc[2])).cropped(to: CGRect(x: 0, y: 0, width: W, height: H))
let thumbCI: [[CIImage]] = thumbs.map { $0.map { CIImage(cgImage: $0) } }

// ---------- writer ----------
try? FileManager.default.removeItem(at: outURL)
let writer = try! AVAssetWriter(outputURL: outURL, fileType: .mp4)
writer.shouldOptimizeForNetworkUse = true
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
  AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: Int(W), AVVideoHeightKey: Int(H),
  AVVideoColorPropertiesKey: [AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2, AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2, AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2],
  AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: bitrate, AVVideoMaxKeyFrameIntervalKey: 60, AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
    AVVideoH264EntropyModeKey: AVVideoH264EntropyModeCABAC, AVVideoExpectedSourceFrameRateKey: film.fps, AVVideoAllowFrameReorderingKey: true]])
input.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
  kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA, kCVPixelBufferWidthKey as String: Int(W), kCVPixelBufferHeightKey as String: Int(H), kCVPixelBufferIOSurfacePropertiesKey as String: [:]])
writer.add(input); writer.startWriting(); writer.startSession(atSourceTime: .zero)

func ease(_ x: Double) -> Double { let t = min(1, max(0, x)); return t < 0.5 ? 4 * t * t * t : 1 - pow(-2 * t + 2, 3) / 2 }
var bloom: (AVAssetReader, AVAssetReaderVideoCompositionOutput, Int)? = nil
var bloomLast: CIImage? = nil
var timeline: [[String: Double]] = []

let shift = Int(((film.beats.first?.stop ?? 0) + openD + 0.6) * fps)
print("SHIFT", Double(shift) / fps)
for oi in 0..<N {
  let i = (oi + shift) % N
  let t = Double(i) / fps
  var img = bg
  // active beat?
  var active: (Int, Double)? = nil  // (beat index, phase 0..1 open, 1 = full, closing handled by p)
  for (bi, b) in film.beats.enumerated() {
    let s = b.stop, e = b.stop + openD + b.hold + closeD
    if t >= s && t < e { active = (bi, t - s) }
  }
  // cards
  for c in 0..<cols {
    let kMin = Int(floor((offsetAt(i) * colSpeed[c] - colPhase[c] * pitch - cardH) / pitch)) - 1
    for k in kMin...(kMin + Int(ceil(H / pitch)) + 3) {
      let yTop = cardY(c, k, i)
      if yTop > H + 10 || yTop + cardH < -10 { continue }
      if let (bi, _) = active, c == mid, k == chosen[bi] { continue }  // drawn as the bloom
      let ci = contentIndex(c, k)
      let tn = max(1, thumbCI[ci].count)
      if thumbCI[ci].isEmpty { continue }
      let fr = thumbCI[ci][(((i / 2) + k * 5 + c * 3) % tn + tn) % tn]
      let x = colX[c], y = H - yTop - cardH  // CI origin bottom-left
      img = shadow.transformed(by: CGAffineTransform(translationX: x, y: y - cardW * 0.035)).composited(over: img)
      let card = fr.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: CIImage.empty(), kCIInputMaskImageKey: cardMask])
      img = card.transformed(by: CGAffineTransform(translationX: x, y: y)).composited(over: img)
    }
  }
  // bloom
  if let (bi, dt) = active {
    let b = film.beats[bi]
    if bloom == nil || bloom!.2 != bi {
      bloom?.0.cancelReading()
      let into = max(0, t - b.stop)
      let (r, o) = await reader(ClipRef(file: b.clip.file, start: b.clip.start + into, fx: b.clip.fx, fy: b.clip.fy, ev: b.clip.ev), openD + b.hold + closeD + 0.6 - into)
      bloom = (r, o, bi); bloomLast = nil
    }
    // play the clip at real time from the stop; the card's own thumbnail was the same clip
    if let sb = bloom!.1.copyNextSampleBuffer(), let pb = CMSampleBufferGetImageBuffer(sb) {
      var im = CIImage(cvPixelBuffer: pb)
      if let ev = b.clip.ev { im = im.applyingFilter("CIExposureAdjust", parameters: ["inputEV": ev]) }
      bloomLast = im
      // 60 fps sources: drop every other frame
      if (CMTimeGetSeconds(CMSampleBufferGetDuration(sb)) < 0.025) { _ = bloom!.1.copyNextSampleBuffer() }
    }
    let open = ease(dt / openD), close = ease((dt - openD - b.hold) / closeD)
    let k = open * (1 - close)
    let yTop = cardY(mid, chosen[bi], i)
    let x0 = colX[mid], y0 = H - yTop - cardH
    let x = x0 * (1 - k), y = y0 * (1 - k), w = cardW + (W - cardW) * k, h = cardH + (H - cardH) * k
    let rr = radius * (1 - k)
    if let src = bloomLast {
      let face = grade(fit(src, w, h, b.clip.fx ?? 0.5, b.clip.fy ?? 0.45))
      let mask = roundRect(w, h, max(0.01, rr))
      let shadowK = 1 - k
      if shadowK > 0.01 {
        let sh = roundRect(w, h, max(0.01, rr)).applyingFilter("CIColorMatrix", parameters: ["inputRVector": CIVector(x: 0, y: 0, z: 0, w: 0), "inputGVector": CIVector(x: 0, y: 0, z: 0, w: 0), "inputBVector": CIVector(x: 0, y: 0, z: 0, w: 0), "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 0.3 * shadowK)])
          .clampedToExtent().applyingFilter("CIGaussianBlur", parameters: ["inputRadius": 30]).cropped(to: CGRect(x: -90, y: -90, width: w + 180, height: h + 180))
        img = sh.transformed(by: CGAffineTransform(translationX: x, y: y - 16)).composited(over: img)
      }
      img = face.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: CIImage.empty(), kCIInputMaskImageKey: mask])
        .transformed(by: CGAffineTransform(translationX: x, y: y)).composited(over: img)
    }

  } else if bloom != nil { bloom?.0.cancelReading(); bloom = nil }

  while !input.isReadyForMoreMediaData { usleep(1000) }
  var opb: CVPixelBuffer? = nil
  CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &opb)
  let o = opb!
  CVBufferSetAttachment(o, kCVImageBufferColorPrimariesKey, kCVImageBufferColorPrimaries_ITU_R_709_2, .shouldPropagate)
  CVBufferSetAttachment(o, kCVImageBufferTransferFunctionKey, kCVImageBufferTransferFunction_ITU_R_709_2, .shouldPropagate)
  CVBufferSetAttachment(o, kCVImageBufferYCbCrMatrixKey, kCVImageBufferYCbCrMatrix_ITU_R_709_2, .shouldPropagate)
  ctx.render(img, to: o, bounds: CGRect(x: 0, y: 0, width: W, height: H), colorSpace: c709)
  _ = adaptor.append(o, withPresentationTime: CMTime(value: Int64(oi), timescale: CMTimeScale(film.fps)))
  if let dir = stillsDir, oi % 30 == 0 {
    if let cg = ctx.createCGImage(img, from: CGRect(x: 0, y: 0, width: W, height: H), format: .RGBA8, colorSpace: srgb) {
      let d = CGImageDestinationCreateWithURL(dir.appendingPathComponent(String(format: "f%04d.jpg", oi)) as CFURL, UTType.jpeg.identifier as CFString, 1, nil)!
      CGImageDestinationAddImage(d, cg, [kCGImageDestinationLossyCompressionQuality: 0.84] as CFDictionary); CGImageDestinationFinalize(d)
    }
  }
}
var beats: [[String: Double]] = []
for b in film.beats {
  let d = Double(N) / fps, sh = Double(shift) / fps
  func o(_ x: Double) -> Double { ((x - sh).truncatingRemainder(dividingBy: d) + d).truncatingRemainder(dividingBy: d) }
  beats.append(["in": o(b.stop + openD * 0.7), "out": o(b.stop + openD + b.hold + closeD * 0.2)])
}
print("BEATS", String(data: try! JSONSerialization.data(withJSONObject: beats), encoding: .utf8)!)
input.markAsFinished()
await writer.finishWriting()
print("DONE", N, "frames", writer.status.rawValue, writer.error as Any)
