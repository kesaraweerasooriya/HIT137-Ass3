import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np
import os
from functools import wraps
import time

# LoggingMixin provides logging functionality to any class that inherits from it
class LoggingMixin:
  def log(self, message):
      print(f"Log: {message}")

# TimingMixin provides timing functionality to measure execution time of methods
class TimingMixin:
  def __init__(self):
      self.start_time = None

  def start_timer(self):
      self.start_time = time.time()

  def end_timer(self):
      if self.start_time:
          elapsed_time = time.time() - self.start_time
          print(f"Elapsed time: {elapsed_time:.2f} seconds")
          self.start_time = None

# Decorator to log method calls
def log_method(func):
  @wraps(func)
  def wrapper(self, *args, **kwargs):
      print(f"Calling method: {func.__name__}")
      return func(self, *args, **kwargs)
  return wrapper

# Decorator to time method execution
def timing_decorator(func):
  @wraps(func)
  def wrapper(self, *args, **kwargs):
      start_time = time.time()
      result = func(self, *args, **kwargs)
      end_time = time.time()
      print(f"{func.__name__} took {end_time - start_time:.2f} seconds to execute")
      return result
  return wrapper

# Main application class using multiple inheritance
class ObjectDetectionApp(tk.Frame, LoggingMixin, TimingMixin):
  def __init__(self, master):
      super().__init__(master)
      LoggingMixin.__init__(self)  # Initialize LoggingMixin
      TimingMixin.__init__(self)   # Initialize TimingMixin
      
      self.master = master
      self.master.title("IMAGE DETECTOR")
      self.master.geometry("1000x700")
      self.master.configure(bg="#f0f0f0")

      # Show a loading screen for 2.5 seconds
      self.show_loading_screen()
      self.master.after(2500, self.initialize_app)

  def show_loading_screen(self):
      # Create a loading screen with a progress bar
      self.loading_frame = tk.Frame(self.master, bg="#f0f0f0")
      self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")

      logo_path = "logo.png"  # Ensure this file exists
      if os.path.exists(logo_path):
          logo = Image.open(logo_path)
          logo = logo.resize((200, 200), Image.LANCZOS)
          logo_photo = ImageTk.PhotoImage(logo)
          logo_label = tk.Label(self.loading_frame, image=logo_photo, bg="#f0f0f0")
          logo_label.image = logo_photo
          logo_label.pack(pady=20)

      self.progress = ttk.Progressbar(self.loading_frame, orient="horizontal", length=300, mode="indeterminate")
      self.progress.pack(pady=20)
      self.progress.start()
      
      self.loading_label = tk.Label(self.loading_frame, text="Loading IMAGE DETECTOR...", bg="#f0f0f0", font=("Arial", 12))
      self.loading_label.pack()

  def initialize_app(self):
      # Initialize the main application after the loading screen
      self.loading_frame.destroy()
      self.model = self.load_model()  # Load the AI model
      self.image_path = None
      self.detection_results = None

      self.create_widgets()  # Create the main interface widgets
      self.style_widgets()   # Style the widgets
      self.load_placeholder_image()  # Load a placeholder image

  # Encapsulation: Private method to load the AI model
  def __load_model(self):
      prototxt_path = "MobileNetSSD_deploy.prototxt.txt"
      model_path = "MobileNetSSD_deploy.caffemodel"
      return cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

  # Method overriding: Public method to load the model, with logging
  def load_model(self):
      self.log("Loading model")
      return self.__load_model()

  @log_method
  @timing_decorator
  def create_widgets(self):
      # Create the main interface widgets
      self.create_header()
      self.create_main_frame()
      self.create_footer()

  def create_header(self):
      # Create the header section
      header_frame = tk.Frame(self.master, bg="#3498db", padx=10, pady=10)
      header_frame.pack(fill=tk.X)

      title_label = tk.Label(header_frame, text="IMAGE DETECTOR", font=("Arial", 24, "bold"), fg="white", bg="#3498db")
      title_label.pack()

  def create_main_frame(self):
      # Create the main content area
      main_frame = tk.Frame(self.master, bg="#f0f0f0", padx=20, pady=20)
      main_frame.pack(expand=True, fill=tk.BOTH)

      left_frame = tk.Frame(main_frame, bg="#f0f0f0")
      left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

      right_frame = tk.Frame(main_frame, bg="#f0f0f0")
      right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

      self.create_image_frame(left_frame)
      self.create_result_frame(right_frame)

  def create_image_frame(self, parent):
      # Create the image display and upload section
      image_frame = tk.Frame(parent, bg="#ffffff", bd=2, relief=tk.GROOVE)
      image_frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

      self.image_label = tk.Label(image_frame, bg="#ffffff", text="No image selected")
      self.image_label.pack(expand=True, fill=tk.BOTH)

      button_frame = tk.Frame(parent, bg="#f0f0f0")
      button_frame.pack(pady=10)

      self.upload_button = tk.Button(button_frame, text="Upload Image", command=self.upload_image)
      self.upload_button.pack(side=tk.LEFT, padx=5)

      self.detect_button = tk.Button(button_frame, text="Detect Objects", command=self.detect_objects)
      self.detect_button.pack(side=tk.LEFT, padx=5)

  def create_result_frame(self, parent):
      # Create the results display section
      self.result_frame = tk.Frame(parent, bg="#ffffff", bd=2, relief=tk.GROOVE)
      self.result_frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

      self.result_label = tk.Label(self.result_frame, text="Detection Results", font=("Arial", 16, "bold"), bg="#ffffff")
      self.result_label.pack(pady=10)

      self.placeholder_label = tk.Label(self.result_frame, bg="#ffffff")
      self.placeholder_label.pack(expand=True, fill=tk.BOTH)

  def create_footer(self):
      # Create the footer section
      footer_frame = tk.Frame(self.master, bg="#3498db", padx=10, pady=5)
      footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

      footer_label = tk.Label(footer_frame, text="© 2024 IMAGE DETECTOR", font=("Arial", 10), fg="white", bg="#3498db")
      footer_label.pack()

  def style_widgets(self):
      # Style the buttons
      self.upload_button.configure(bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5, bd=0)
      self.detect_button.configure(bg="#2196F3", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5, bd=0)

  def load_placeholder_image(self):
      # Load a placeholder image
      try:
          image = Image.open("placeholder.png")
          image = image.resize((300, 300), Image.LANCZOS)
          photo = ImageTk.PhotoImage(image)
          self.placeholder_label.config(image=photo)
          self.placeholder_label.image = photo
      except FileNotFoundError:
          self.log("Placeholder image not found. Using text instead.")
          self.placeholder_label.config(text="Placeholder Image")

  @log_method
  def upload_image(self):
      # Upload an image for detection
      self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
      if self.image_path:
          image = Image.open(self.image_path)
          image.thumbnail((400, 400))
          photo = ImageTk.PhotoImage(image)
          self.image_label.config(image=photo)
          self.image_label.image = photo

  @log_method
  @timing_decorator
  def detect_objects(self):
      # Detect objects in the uploaded image
      if self.image_path is None:
          messagebox.showerror("Error", "Please upload an image first.")
          return

      self.show_detection_screen()
      self.master.after(2000, self.process_detection)

  def show_detection_screen(self):
      # Show a loading screen while detecting objects
      for widget in self.result_frame.winfo_children():
          widget.destroy()

      self.detection_canvas = tk.Canvas(self.result_frame, bg="#ffffff")
      self.detection_canvas.pack(expand=True, fill=tk.BOTH)

      self.detection_canvas.create_text(
          self.result_frame.winfo_width() // 2,
          self.result_frame.winfo_height() // 2,
          text="Detecting Objects...",
          font=("Arial", 24, "bold"),
          fill="#3498db"
      )

      self.loading_oval = self.detection_canvas.create_oval(
          self.result_frame.winfo_width() // 2 - 25,
          self.result_frame.winfo_height() // 2 + 40,
          self.result_frame.winfo_width() // 2 + 25,
          self.result_frame.winfo_height() // 2 + 90,
          outline="#3498db",
          width=3
      )
      self.animate_loading()

      self.master.update()

  def animate_loading(self):
      # Animate the loading indicator
      if not hasattr(self, 'detection_canvas') or not self.detection_canvas.winfo_exists():
          return

      try:
          current_width = self.detection_canvas.itemcget(self.loading_oval, 'width')
          new_width = 6 if float(current_width) <= 3 else 3
          self.detection_canvas.itemconfig(self.loading_oval, width=new_width)
          self.master.after(300, self.animate_loading)
      except tk.TclError:
          pass

  @timing_decorator
  def process_detection(self):
      # Process the image for object detection
      image = cv2.imread(self.image_path)
      (h, w) = image.shape[:2]
      blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

      self.model.setInput(blob)
      detections = self.model.forward()

      self.detection_results = []
      for i in range(detections.shape[2]):
          confidence = detections[0, 0, i, 2]
          if confidence > 0.5:
              idx = int(detections[0, 0, i, 1])
              box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
              (startX, startY, endX, endY) = box.astype("int")
              self.detection_results.append((CLASSES[idx], confidence, (startX, startY, endX, endY)))

      self.display_results()

  def display_results(self):
      # Display the detection results
      for widget in self.result_frame.winfo_children():
          widget.destroy()

      canvas = tk.Canvas(self.result_frame, bg="#ffffff")
      canvas.pack(expand=True, fill=tk.BOTH)

      try:
          overlay_image = Image.open("jumping_boy.png")
          overlay_image = overlay_image.resize((200, 200), Image.LANCZOS)
          overlay_photo = ImageTk.PhotoImage(overlay_image)
          canvas.create_image(10, 10, anchor=tk.NW, image=overlay_photo)
          canvas.image = overlay_photo
      except FileNotFoundError:
          self.log("Overlay image (jumping_boy.png) not found. Skipping overlay.")

      y_offset = 220  # Start text below the jumping boy image
      for obj, confidence, box in self.detection_results:
          result_text = f"{obj}: {confidence:.2f}"
          canvas.create_text(10, y_offset, anchor=tk.NW, text=result_text, font=("Arial", 16, "bold"))
          y_offset += 30

      image = Image.open(self.image_path)
      draw = ImageDraw.Draw(image)
      for obj, confidence, box in self.detection_results:
          draw.rectangle(box, outline="red", width=2)
          draw.text((box[0], box[1] - 10), f"{obj}: {confidence:.2f}", fill="red")

      image.thumbnail((400, 400))
      photo = ImageTk.PhotoImage(image)
      self.image_label.config(image=photo)
      self.image_label.image = photo

# List of class labels for the object detection model
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
         "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

if __name__ == "__main__":
  root = tk.Tk()
  app = ObjectDetectionApp(root)
  root.mainloop()