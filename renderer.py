import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import numpy as np

class Renderer:
    def __init__(self, master, filename):
        self.master = master
        
        # Create a canvas to draw on
        self.canvas = tk.Canvas(master, width=800, height=600)
        self.canvas.pack()

        # Create a blank image to draw the 3D object on
        self.image = Image.new('RGB', (800, 600), color='#FFFFFF')
        self.draw = ImageDraw.Draw(self.image)
        self.photo = None  # Will hold the PhotoImage for display on canvas

        # Initialize rotation matrix as identity (no rotation)
        self.rotation_matrix = np.eye(3)
        
        # Store last mouse position for rotation calculations
        self.last_x = 0
        self.last_y = 0

        # Read the 3D object data from the specified file
        self.vertices, self.faces = self.read_object_file(filename)

        # Bind mouse events for rotation
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

    def read_object_file(self, filename):
        vertices = {}
        faces = []
        with open(filename, 'r') as file:
            # Read the number of vertices and faces from the first line
            num_vertices, num_faces = map(int, file.readline().strip().split(','))
            
            # Read vertex data
            for _ in range(num_vertices):
                line = file.readline().strip().split(',')
                vertex_id = int(line[0])
                # Convert x, y, z coordinates to floats and scale up
                x, y, z = map(float, line[1:])
                vertices[vertex_id] = np.array([x, y, z]) * 100  # Scale up for better visibility
            
            # Read face data
            for _ in range(num_faces):
                # Each face is defined by a list of vertex IDs
                face = list(map(int, file.readline().strip().split(',')))
                faces.append(face)

        return vertices, faces

    def on_mouse_down(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def on_mouse_drag(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        
        # Calculate rotation axis and angle
        # Invert both x and y rotations
        rotation_axis = np.array([-dy, -dx, 0])
        rotation_angle = np.linalg.norm(rotation_axis) * 0.01

        if np.any(rotation_axis):
            rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
            
            # Create rotation matrix using Rodrigues' rotation formula
            c = np.cos(rotation_angle)
            s = np.sin(rotation_angle)
            t = 1 - c
            x, y, z = rotation_axis
            rotation = np.array([
                [t*x*x + c, t*x*y - z*s, t*x*z + y*s],
                [t*x*y + z*s, t*y*y + c, t*y*z - x*s],
                [t*x*z - y*s, t*y*z + x*s, t*z*z + c]
            ])
            
            # Update the cumulative rotation matrix
            self.rotation_matrix = np.dot(rotation, self.rotation_matrix)

        self.last_x = event.x
        self.last_y = event.y
        self.render()

    def rotate_point(self, point):
        return np.dot(point, self.rotation_matrix.T)

    def project(self, point):
        return (int(point[0] + 400), int(-point[1] + 300))

    def calculate_normal(self, face):
        v0, v1, v2 = [self.rotated_vertices[i] for i in face[:3]]
        edge1 = v1 - v0
        edge2 = v2 - v0
        return np.cross(edge1, edge2)

    def normalize(self, vector):
        norm = np.linalg.norm(vector)
        return vector / norm if norm != 0 else vector

    def calculate_color(self, normal):
        z_axis = np.array([0, 0, 1])
        normal_normalized = self.normalize(normal)
        cos_angle = abs(np.dot(normal_normalized, z_axis))
        
        # Interpolate between #00005F and #0000FF
        blue = int(0x5F + (0xFF - 0x5F) * cos_angle)
        return f'#0000{blue:02X}'

    def render(self):
        # Clear the image
        self.draw.rectangle([0, 0, 800, 600], fill='#FFFFFF')

        # Rotate vertices
        self.rotated_vertices = {k: self.rotate_point(v) for k, v in self.vertices.items()}

        # Sort faces by depth (simple painter's algorithm)
        sorted_faces = sorted(self.faces, 
                              key=lambda face: np.mean([self.rotated_vertices[i][2] for i in face]), 
                              reverse=True)

        # Draw faces with shading
        for face in sorted_faces:
            normal = self.calculate_normal(face)
            color = self.calculate_color(normal)
            
            # Project vertices of the face
            projected_vertices = [self.project(self.rotated_vertices[i]) for i in face]
            
            # Draw the face
            self.draw.polygon(projected_vertices, fill=color, outline='#000000')

        # Update the canvas
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)

# Get filename from user
filename = input("Enter the filename of the 3D object: ")

root = tk.Tk()
root.title("3D Object Renderer")
renderer = Renderer(root, filename)
renderer.render()
root.mainloop()