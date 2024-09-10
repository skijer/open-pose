import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os

mp_drawing = mp.solutions.drawing_utils 
mp_pose = mp.solutions.pose

def detect_pose(frame, pose_model):
    # Convertir la imagen a escala de grises
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detectar la pose en la imagen
    try:
        results = pose_model.process(image_rgb)
        if results.pose_landmarks:
            return results.pose_landmarks
        else:
            return None
    except:
        return None

    

def message_files(path):
    def disable_event():
        pass
    def close_window(higher):
        higher.destroy()
    panel = tk.Tk()
    panel.title("Procesando archivos")
    panel.protocol("WM_DELETE_WINDOW", disable_event)
    label = tk.Label(panel, text="Leyendo archivo: "+path)
    label.pack(pady=20)
    panel.overrideredirect(True)
    
    cap = cv2.VideoCapture(path)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    pose_data=[]
    pose_model = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    with mp_pose.Pose(static_image_mode=False) as pose:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detectar la pose en el cuadro actual
            pose_landmarks = detect_pose(frame, pose_model)
            
            # Guardar los puntos de la pose en la lista
            if pose_landmarks:
                # Convertir landmarks a un diccionario
                landmarks_dict = {}
                mp_drawing.draw_landmarks(frame, pose_landmarks, mp_pose.POSE_CONNECTIONS)
                for i, landmark in enumerate(pose_landmarks.landmark):
                    landmarks_dict[f"landmark_{i}_x"] = int(landmark.x * frame_width)
                    landmarks_dict[f"landmark_{i}_y"] = int(landmark.y * frame_height)
                    landmarks_dict[f"landmark_{i}_z"] = landmark.z
                pose_data.append(landmarks_dict)
            
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    
    # Convertir los datos de la pose a un DataFrame de pandas
    df = pd.DataFrame(pose_data)

    # Guardar los datos en un archivo CSV
    csv_filename = os.path.basename(path) + ".csv"
    df.to_csv(csv_filename, index=False)
    print("Datos de la pose guardados en:", csv_filename)



# Crear una instancia de Tkinter
root = tk.Tk()
root.withdraw()

file_paths = filedialog.askopenfilenames(title="Selecciona los videos para abrir")

# Mostrar las rutas de los archivos seleccionados
for file_path in file_paths:
    message_files(file_path)
