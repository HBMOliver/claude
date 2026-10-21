// Crop to an aspect around a focus point, resize, write JPEG.
// usage: img <in> <out.jpg> <w> <h> [fx] [fy] [zoom] [quality] [gray]
import Foundation
import CoreImage
import ImageIO
import UniformTypeIdentifiers
let a = CommandLine.arguments
let W = Double(a[3])!, H = Double(a[4])!
let fx = a.count > 5 ? Double(a[5])! : 0.5, fy = a.count > 6 ? Double(a[6])! : 0.5
let zoom = a.count > 7 ? Double(a[7])! : 1, q = a.count > 8 ? Double(a[8])! : 0.82
let gray = a.count > 9 && a[9] == "gray"
var img = CIImage(contentsOf: URL(fileURLWithPath: a[1]), options: [.applyOrientationProperty: true])!
let iw = img.extent.width, ih = img.extent.height
let asp = W / H
var cw = Double(iw), ch = Double(iw) / asp
if Double(iw) / Double(ih) > asp { ch = Double(ih); cw = Double(ih) * asp }
cw /= zoom; ch /= zoom
let cx = min(max(fx * Double(iw), cw / 2), Double(iw) - cw / 2)
let cy = min(max(Double(ih) - fy * Double(ih), ch / 2), Double(ih) - ch / 2)
img = img.cropped(to: CGRect(x: cx - cw / 2, y: cy - ch / 2, width: cw, height: ch))
  .transformed(by: CGAffineTransform(translationX: -(cx - cw / 2), y: -(cy - ch / 2)))
img = img.clampedToExtent().applyingFilter("CILanczosScaleTransform", parameters: ["inputScale": W / cw, "inputAspectRatio": 1.0])
  .cropped(to: CGRect(x: 0, y: 0, width: W, height: H))
if gray { img = img.applyingFilter("CIPhotoEffectMono") }
let ctx = CIContext()
let cs = CGColorSpace(name: CGColorSpace.sRGB)!
let cg = ctx.createCGImage(img, from: CGRect(x: 0, y: 0, width: W, height: H), format: .RGBA8, colorSpace: cs)!
let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: a[2]) as CFURL, UTType.jpeg.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(d, cg, [kCGImageDestinationLossyCompressionQuality: q] as CFDictionary)
CGImageDestinationFinalize(d)
