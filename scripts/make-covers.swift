#!/usr/bin/env swift
// Draws the blog's covers: the picture a link to a post shows (og:image) and the card on the
// blog's list. 1200 × 630, in the Slate look of the app and the site: the post's eyebrow and
// title on the left, the mark and the name below them, and the first phone screen the post
// shows on the right, from blog/media (scripts/update-blog-media.py puts it there first). A post
// can name another with <meta name="tp:cover-screen" content="media/iphone/….jpg">.
//
//   swift scripts/make-covers.swift            every post in _drafts/ and blog/
//   swift scripts/make-covers.swift <slug> …   those posts
//
//   → blog/media/covers/<slug>.jpg, as JPEG: a link preview is fetched by every app it's shared to
import AppKit

let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
let fm = FileManager.default
let size = CGSize(width: 1200, height: 630)
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!

func rgb(_ hex: UInt32, _ alpha: CGFloat = 1) -> NSColor {
    NSColor(srgbRed: CGFloat((hex >> 16) & 0xFF) / 255, green: CGFloat((hex >> 8) & 0xFF) / 255,
            blue: CGFloat(hex & 0xFF) / 255, alpha: alpha)
}

// Slate (Branding/BRAND.md in the app repository)
let ground = rgb(0x222831), deep = rgb(0x1A1E24), text = rgb(0xEEEEEE), muted = rgb(0xB5BCC4)
let teal = rgb(0x76ABAE), steel = rgb(0x909D9E)

struct Post {
    let slug: String
    let title: String
    let eyebrow: String
    let screen: URL?
}

func firstMatch(_ pattern: String, in text: String) -> String? {
    guard let regex = try? NSRegularExpression(pattern: pattern, options: [.dotMatchesLineSeparators]),
          let match = regex.firstMatch(in: text, range: NSRange(text.startIndex..., in: text)),
          let range = Range(match.range(at: 1), in: text) else { return nil }
    return String(text[range])
}

func plain(_ html: String) -> String {
    let stripped = html.replacingOccurrences(of: "<[^>]+>", with: "", options: .regularExpression)
    let data = Data(stripped.utf8)
    let decoded = try? NSAttributedString(data: data, options: [.documentType: NSAttributedString.DocumentType.html,
                                                                .characterEncoding: String.Encoding.utf8.rawValue],
                                          documentAttributes: nil)
    return (decoded?.string ?? stripped).trimmingCharacters(in: .whitespacesAndNewlines)
}

func posts(_ wanted: [String]) -> [Post] {
    var found: [Post] = []
    for folder in ["_drafts", "blog"] {
        let dir = root.appendingPathComponent(folder)
        let names = ((try? fm.contentsOfDirectory(atPath: dir.path)) ?? []).filter { $0.hasSuffix(".html") && $0 != "index.html" }
        for name in names.sorted() {
            let slug = String(name.dropLast(5))
            guard wanted.isEmpty || wanted.contains(slug),
                  let html = try? String(contentsOf: dir.appendingPathComponent(name), encoding: .utf8) else { continue }
            let title = plain(firstMatch("<h1[^>]*>(.*?)</h1>", in: html) ?? slug)
            let eyebrow = plain(firstMatch("<p class=\"eyebrow\">(.*?)</p>", in: html) ?? "")
            // The screen the post names for its cover (<meta name="tp:cover-screen" content="media/…">),
            // else its first phone screen: a capture of the iPhone, or a program's on the iPhone
            let screen = firstMatch("<meta name=\"tp:cover-screen\" content=\"(media/[^\"]+\\.jpg)\">", in: html)
                ?? firstMatch("src=\"(media/(?:iphone/[^\"]+|programs/[^\"]+/iphone-[^\"]+)\\.jpg)\"", in: html)
                ?? firstMatch("poster=\"(media/clips/iphone/[^\"]+\\.jpg)\"", in: html)
            found.append(Post(slug: slug, title: title, eyebrow: eyebrow,
                              screen: screen.map { root.appendingPathComponent("blog").appendingPathComponent($0) }))
        }
    }
    return found
}

/// The mark: three rising bars and the chevron over the tallest, in its 729-unit square.
func drawMark(in rect: CGRect, context ctx: CGContext) {
    let scale = rect.width / 729
    func point(_ x: CGFloat, _ y: CGFloat) -> CGPoint {
        // SVG units (origin top-left, viewBox from 180, 131) to the context's (origin bottom-left)
        CGPoint(x: rect.minX + (x - 180) * scale, y: rect.maxY - (y - 131) * scale)
    }
    let bars: [(CGFloat, CGFloat, CGFloat, CGFloat, NSColor)] = [
        (212, 620, 150, 240, steel), (437, 470, 150, 390, teal), (662, 320, 150, 540, text)]
    for (x, y, w, h, color) in bars {
        let origin = point(x, y + h)
        let bar = CGRect(x: origin.x, y: origin.y, width: w * scale, height: h * scale)
        ctx.addPath(CGPath(roundedRect: bar, cornerWidth: 42 * scale, cornerHeight: 42 * scale, transform: nil))
        ctx.setFillColor(color.cgColor)
        ctx.fillPath()
    }
    ctx.setStrokeColor(text.cgColor)
    ctx.setLineWidth(58 * scale)
    ctx.setLineCap(.round)
    ctx.setLineJoin(.round)
    ctx.move(to: point(625, 260))
    ctx.addLine(to: point(737, 160))
    ctx.addLine(to: point(849, 260))
    ctx.strokePath()
}

func glow(_ ctx: CGContext, center: CGPoint, radius: CGFloat, color: NSColor) {
    let colors = [color.cgColor, color.withAlphaComponent(0).cgColor] as CFArray
    guard let gradient = CGGradient(colorsSpace: srgb, colors: colors, locations: [0, 1]) else { return }
    ctx.drawRadialGradient(gradient, startCenter: center, startRadius: 0, endCenter: center, endRadius: radius, options: [])
}

/// The title in the largest size, from 66 down, that fits four lines of the width.
func titleText(_ title: String, width: CGFloat) -> NSAttributedString {
    var fontSize: CGFloat = 66
    while true {
        let paragraph = NSMutableParagraphStyle()
        paragraph.lineBreakMode = .byWordWrapping
        paragraph.lineHeightMultiple = 0.98
        let attributed = NSAttributedString(string: title, attributes: [
            .font: NSFont.systemFont(ofSize: fontSize, weight: .heavy), .foregroundColor: text,
            .paragraphStyle: paragraph, .kern: -fontSize * 0.02])
        let height = attributed.boundingRect(with: CGSize(width: width, height: 2000),
                                             options: [.usesLineFragmentOrigin, .usesFontLeading]).height
        if height <= fontSize * 1.05 * 4 || fontSize <= 36 { return attributed }
        fontSize -= 2
    }
}

func draw(_ post: Post) -> Data? {
    guard let ctx = CGContext(data: nil, width: Int(size.width), height: Int(size.height), bitsPerComponent: 8,
                              bytesPerRow: 0, space: srgb, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { return nil }
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(cgContext: ctx, flipped: false)

    // The ground, with the site's two glows
    let colors = [ground.cgColor, deep.cgColor] as CFArray
    if let gradient = CGGradient(colorsSpace: srgb, colors: colors, locations: [0, 1]) {
        ctx.drawLinearGradient(gradient, start: CGPoint(x: 0, y: size.height), end: CGPoint(x: 0, y: 0), options: [])
    }
    glow(ctx, center: CGPoint(x: 1050, y: 640), radius: 620, color: teal.withAlphaComponent(0.22))
    glow(ctx, center: CGPoint(x: -80, y: -60), radius: 520, color: teal.withAlphaComponent(0.14))

    // The phone screen, on the right, running off the bottom edge
    if let url = post.screen, let image = NSImage(contentsOf: url),
       let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) {
        let width: CGFloat = 330
        let height = width * CGFloat(cg.height) / CGFloat(cg.width)
        let frame = CGRect(x: 800, y: size.height - 64 - height, width: width, height: height)
        ctx.saveGState()
        ctx.setShadow(offset: CGSize(width: 0, height: -18), blur: 44, color: NSColor.black.withAlphaComponent(0.55).cgColor)
        let shape = CGPath(roundedRect: frame, cornerWidth: 38, cornerHeight: 38, transform: nil)
        ctx.addPath(shape)
        ctx.setFillColor(deep.cgColor)
        ctx.fillPath()
        ctx.restoreGState()
        ctx.saveGState()
        ctx.addPath(shape)
        ctx.clip()
        ctx.draw(cg, in: frame)
        ctx.restoreGState()
        ctx.addPath(shape)
        ctx.setStrokeColor(NSColor.white.withAlphaComponent(0.14).cgColor)
        ctx.setLineWidth(2)
        ctx.strokePath()
    }

    // The words, on the left
    let left: CGFloat = 72
    let width: CGFloat = post.screen == nil ? 1056 : 660
    let eyebrow = NSAttributedString(string: post.eyebrow.uppercased(), attributes: [
        .font: NSFont.systemFont(ofSize: 22, weight: .bold), .foregroundColor: teal, .kern: 2.6])
    eyebrow.draw(at: CGPoint(x: left, y: size.height - 96))
    let title = titleText(post.title, width: width)
    let titleHeight = title.boundingRect(with: CGSize(width: width, height: 2000),
                                         options: [.usesLineFragmentOrigin, .usesFontLeading]).height
    title.draw(with: CGRect(x: left, y: size.height - 124 - titleHeight, width: width, height: titleHeight),
               options: [.usesLineFragmentOrigin, .usesFontLeading])

    // The mark and the name, at the foot
    drawMark(in: CGRect(x: left, y: 56, width: 46, height: 46), context: ctx)
    let name = NSAttributedString(string: "TrainingPlanner", attributes: [
        .font: NSFont.systemFont(ofSize: 28, weight: .heavy), .foregroundColor: text, .kern: -0.5])
    name.draw(at: CGPoint(x: left + 62, y: 62))
    let site = NSAttributedString(string: "trainingplanner.pro", attributes: [
        .font: NSFont.systemFont(ofSize: 22, weight: .semibold), .foregroundColor: muted])
    site.draw(at: CGPoint(x: left + 300, y: 66))

    NSGraphicsContext.restoreGraphicsState()
    guard let image = ctx.makeImage() else { return nil }
    return NSBitmapImageRep(cgImage: image).representation(using: .jpeg, properties: [.compressionFactor: 0.86])
}

let wanted = Array(CommandLine.arguments.dropFirst())
let output = root.appendingPathComponent("blog/media/covers")
try? fm.createDirectory(at: output, withIntermediateDirectories: true)
var written = 0
for post in posts(wanted) {
    if post.screen.map({ !fm.fileExists(atPath: $0.path) }) ?? true {
        print("\(post.slug): its phone screen isn't in blog/media yet; drawn without it")
    }
    guard let data = draw(Post(slug: post.slug, title: post.title, eyebrow: post.eyebrow,
                               screen: post.screen.flatMap { fm.fileExists(atPath: $0.path) ? $0 : nil })) else { continue }
    try data.write(to: output.appendingPathComponent("\(post.slug).jpg"))
    written += 1
}
print("\(written) covers in blog/media/covers")
