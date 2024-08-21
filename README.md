# 3D Object Renderer

A simple Python program that renders 3D objects from text file descriptions using Tkinter and Pillow.

## Features

- Reads 3D object data from text files
- Renders objects as wireframes with basic shading
- Allows rotation of objects with mouse interaction
- Supports objects with triangular faces

## Requirements

- Python 3.x
- Tkinter (usually comes with Python)
- Pillow
- NumPy

## Usage

1. Ensure all requirements are installed.
2. Run the script: renderer.py
3. When prompted, enter the name of the object file (e.g., "object.txt").
4. Click and drag in the window to rotate the object.

## Object File Format

- First line: `<number of vertices>,<number of faces>`
- Vertex lines: `<vertex id>,<x>,<y>,<z>`
- Face lines: `<vertex id 1>,<vertex id 2>,<vertex id 3>`

## Example Object Files

- object.txt
- octahedron.txt
- icosahedron.txt