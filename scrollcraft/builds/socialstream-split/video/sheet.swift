// Contact sheets + probe for a list of video files.
// usage: sheet <outdir> <framesPerClip> <clipsPerSheet> <file>...
import Foundation
import AVFoundation
import AppKit

let args = CommandLine.arguments
let outDir = URL(fileURLWithPath: args[1])
let perClip = Int(args[2])!
let perSheet = Int(args[3])!
let files = Array(args.dropFirst(4))

struct Row { let name: String; let info: String; let frames: [CGImage?]; var stamps: [Double] = [] }

func probe(_ spec: String) async -> Row {
  var path = spec; var t0 = -1.0; var t1 = -1.0
  if let at = spec.range(of: "@", options: .backwards) { path = String(spec[..<at.lowerBound]); let r = spec[at.upperBound...].split(separator: "-"); t0 = Double(r[0])!; t1 = Double(r[1])! }
  let url = URL(fileURLWithPath: path)
  let asset = AVURLAsset(url: url)
  var info = ""
  var frames: [CGImage?] = []
  var stamps: [Double] = []
  do {
    let dur = try await asset.load(.duration).seconds
    let tracks = try await asset.loadTracks(withMediaType: .video)
    guard let vt = tracks.first else { return Row(name: url.lastPathComponent, info: "no video", frames: []) }
    let size = try await vt.load(.naturalSize)
    let tf = try await vt.load(.preferredTransform)
    let fps = try await vt.load(.nominalFrameRate)
    let fds = try await vt.load(.formatDescriptions)
    var transfer = "?"
    if let fd = fds.first, let ext = CMFormatDescriptionGetExtensions(fd) as? [String: Any] {
      transfer = (ext[kCVImageBufferTransferFunctionKey as String] as? String) ?? "-"
    }
    let r = CGRect(origin: .zero, size: size).applying(tf)
    let w = Int(abs(r.width)), h = Int(abs(r.height))
    info = String(format: "%.1fs %dx%d %.0ffps %@", dur, w, h, fps, transfer.replacingOccurrences(of: "ITU_R_", with: "").replacingOccurrences(of: "SMPTE_ST_2084_PQ", with: "PQ"))
    print("PROBE\t\(url.lastPathComponent)\t\(dur)\t\(w)\t\(h)\t\(fps)\t\(transfer)")
    let gen = AVAssetImageGenerator(asset: asset)
    gen.appliesPreferredTrackTransform = true
    gen.maximumSize = CGSize(width: 320, height: 320)
    gen.requestedTimeToleranceBefore = CMTime(seconds: 0.1, preferredTimescale: 600)
    gen.requestedTimeToleranceAfter = CMTime(seconds: 0.1, preferredTimescale: 600)
    for i in 0..<perClip {
      let a = t0 >= 0 ? t0 : 0.0, b = t1 >= 0 ? min(t1, dur) : dur
      let t = a + (b - a) * (Double(i) + 0.5) / Double(perClip)
      stamps.append(t)
      let img = try? await gen.image(at: CMTime(seconds: t, preferredTimescale: 600)).image
      frames.append(img)
    }
  } catch { info = "ERR \(error)" }
  return Row(name: url.lastPathComponent, info: info, frames: frames, stamps: stamps)
}

let cell: CGFloat = 200, labelW: CGFloat = 230, rowH: CGFloat = 214
func render(_ rows: [Row], _ idx: Int) {
  let W = labelW + CGFloat(perClip) * cell, H = CGFloat(rows.count) * rowH
  let cs = CGColorSpace(name: CGColorSpace.sRGB)!
  let ctx = CGContext(data: nil, width: Int(W), height: Int(H), bitsPerComponent: 8, bytesPerRow: 0, space: cs, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
  ctx.setFillColor(CGColor(gray: 0.12, alpha: 1)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
  let ns = NSGraphicsContext(cgContext: ctx, flipped: false)
  NSGraphicsContext.current = ns
  for (ri, row) in rows.enumerated() {
    let y0 = H - CGFloat(ri + 1) * rowH
    let attrs: [NSAttributedString.Key: Any] = [.font: NSFont.boldSystemFont(ofSize: 15), .foregroundColor: NSColor.white]
    let attrs2: [NSAttributedString.Key: Any] = [.font: NSFont.systemFont(ofSize: 13), .foregroundColor: NSColor(white: 0.8, alpha: 1)]
    NSString(string: row.name).draw(in: CGRect(x: 8, y: y0 + rowH - 60, width: labelW - 12, height: 50), withAttributes: attrs)
    NSString(string: row.info).draw(in: CGRect(x: 8, y: y0 + 40, width: labelW - 12, height: 60), withAttributes: attrs2)
    for (fi, f) in row.frames.enumerated() {
      guard let f = f else { continue }
      let iw = CGFloat(f.width), ih = CGFloat(f.height)
      let s = min((cell - 8) / iw, (rowH - 8) / ih)
      let dw = iw * s, dh = ih * s
      let x = labelW + CGFloat(fi) * cell + (cell - dw) / 2, y = y0 + (rowH - dh) / 2
      ctx.draw(f, in: CGRect(x: x, y: y, width: dw, height: dh))
      NSString(string: fi < row.stamps.count ? String(format: "%.2f", row.stamps[fi]) : "\(fi)").draw(at: CGPoint(x: labelW + CGFloat(fi) * cell + 6, y: y0 + 6), withAttributes: attrs2)
    }
  }
  NSGraphicsContext.current = nil
  let img = ctx.makeImage()!
  let url = outDir.appendingPathComponent(String(format: "sheet-%02d.jpg", idx))
  let dest = CGImageDestinationCreateWithURL(url as CFURL, "public.jpeg" as CFString, 1, nil)!
  CGImageDestinationAddImage(dest, img, [kCGImageDestinationLossyCompressionQuality: 0.82] as CFDictionary)
  CGImageDestinationFinalize(dest)
  print("SHEET\t\(url.path)")
}

var rows: [Row] = []
var sheet = 0
for f in files {
  rows.append(await probe(f))
  if rows.count == perSheet { render(rows, sheet); sheet += 1; rows = [] }
}
if !rows.isEmpty { render(rows, sheet) }
