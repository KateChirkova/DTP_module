const fs = require("fs")
const path = require("path")

const root = path.join(__dirname, "..")

const rm = (dir) => {
  if (!fs.existsSync(dir)) return
  try {
    fs.rmSync(dir, {
      recursive: true,
      force: true,
      maxRetries: 8,
      retryDelay: 50,
    })
    console.log("removed:", dir)
  } catch {
    try {
      fs.rmSync(dir, { recursive: true, force: true })
      console.log("removed:", dir)
    } catch (e) {
      console.warn("could not remove (close dev server / IDE):", dir, e && e.message)
    }
  }
}

const dirs = [
  ".next",
  ".turbo",
  path.join("node_modules", ".cache"),
  path.join("node_modules", ".cache", "swc"),
  path.join("node_modules", ".cache", "babel-loader"),
]

for (const name of dirs) {
  rm(path.join(root, name))
}
