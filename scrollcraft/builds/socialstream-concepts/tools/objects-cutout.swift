// swift tools/objects-cutout.swift <in.png> <out.png>
// Cuts a generated object out of its plain background with Apple's Vision framework (on this Mac, nothing is uploaded)
// and writes it as a PNG with a transparent background, the same size as the input. For renders made on an opaque
// background (Figma AI's image models have no transparent option); the 2026-11-11 renders came transparent already.
import Foundation
import Vision
import CoreImage

let args = CommandLine.arguments
guard args.count == 3, let input = CIImage(contentsOf: URL(fileURLWithPath: args[1])) else {
  print("usage: objects-cutout <in.png> <out.png>"); exit(1)
}
let handler = VNImageRequestHandler(ciImage: input)
let request = VNGenerateForegroundInstanceMaskRequest()
do { try handler.perform([request]) } catch { print("vision failed:", error); exit(1) }
guard let found = request.results?.first, !found.allInstances.isEmpty else { print("no subject found in", args[1]); exit(1) }
// every instance it finds is kept: an object and its small badge are often two
let masked = try found.generateMaskedImage(ofInstances: found.allInstances, from: handler, croppedToInstancesExtent: false)
let out = CIImage(cvPixelBuffer: masked)
try CIContext().writePNGRepresentation(of: out, to: URL(fileURLWithPath: args[2]), format: .RGBA8,
                                       colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
print("cut", (args[1] as NSString).lastPathComponent, "instances", found.allInstances.count)
