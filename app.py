import sys
import time

import cv2
import mediapipe as mp

WINDOW_NAME = "Ma Vision IA"
INDEX_TIP = 8  # Repère MediaPipe du bout de l'index

# Taille et marge du bouton QUITTER (en pixels)
BUTTON_W, BUTTON_H, BUTTON_MARGIN = 130, 40, 10
COLOR_IDLE = (0, 0, 255)     # Rouge (BGR)
COLOR_HOVER = (0, 200, 0)    # Vert quand l'index survole le bouton

# Initialisation
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERREUR : impossible d'ouvrir la webcam.")
    print("Vérifie qu'elle est branchée, qu'aucune autre application ne l'utilise "
          "et que Python a l'autorisation d'accéder à la caméra.")
    hands.close()
    sys.exit(1)

# État partagé avec le callback souris
state = {"button": (0, 0, 0, 0), "quit": False}


def button_rect(frame):
    """Calcule le rectangle du bouton en haut à droite, d'après la taille de l'image."""
    h, w = frame.shape[:2]
    x2 = w - BUTTON_MARGIN
    x1 = x2 - BUTTON_W
    y1 = BUTTON_MARGIN
    y2 = y1 + BUTTON_H
    return x1, y1, x2, y2


def inside(x, y, rect):
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2


def on_mouse(event, x, y, flags, param):
    # Clic gauche sur le bouton = demande d'arrêt
    if event == cv2.EVENT_LBUTTONDOWN and inside(x, y, state["button"]):
        state["quit"] = True


cv2.namedWindow(WINDOW_NAME)
cv2.setMouseCallback(WINDOW_NAME, on_mouse)

print("Système en ligne. Pour quitter : touche 'Q', croix de la fenêtre, "
      "clic sur QUITTER ou bout de l'index sur QUITTER.")

prev_time = time.perf_counter()
fps = 0.0

try:
    while True:
        success, frame = cap.read()
        if not success:
            print("ERREUR : la webcam ne renvoie plus d'image.")
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        state["button"] = button_rect(frame)
        finger_on_button = False

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

                # Position du bout de l'index en pixels
                tip = hand_lms.landmark[INDEX_TIP]
                tip_x, tip_y = int(tip.x * w), int(tip.y * h)
                cv2.circle(frame, (tip_x, tip_y), 8, (255, 255, 0), -1)
                if inside(tip_x, tip_y, state["button"]):
                    finger_on_button = True

        # --- BOUTON VIRTUEL (index ou souris) ---
        x1, y1, x2, y2 = state["button"]
        color = COLOR_HOVER if finger_on_button else COLOR_IDLE
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
        cv2.putText(frame, "QUITTER (Q)", (x1 + 10, y1 + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # --- IMAGES PAR SECONDE (moyenne lissée) ---
        now = time.perf_counter()
        instant_fps = 1.0 / max(now - prev_time, 1e-6)
        fps = instant_fps if fps == 0.0 else 0.9 * fps + 0.1 * instant_fps
        prev_time = now
        cv2.putText(frame, f"FPS : {fps:.0f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow(WINDOW_NAME, frame)

        if finger_on_button:
            print("\n--- ARRÊT DEMANDÉ (index sur QUITTER) ---")
            cv2.waitKey(300)  # Laisse voir le bouton passer au vert
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n--- ARRÊT DEMANDÉ (touche Q) ---")
            break

        if state["quit"]:
            print("\n--- ARRÊT DEMANDÉ (clic sur QUITTER) ---")
            break

        # Fenêtre fermée avec la croix
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            print("\n--- ARRÊT DEMANDÉ (fenêtre fermée) ---")
            break
finally:
    # --- PROCÉDURE DE DÉCONNEXION ---
    cap.release()  # Libère la webcam
    hands.close()  # Libère le modèle MediaPipe
    cv2.destroyAllWindows()  # Ferme toutes les fenêtres
    print("Caméra désactivée avec succès. Confidentialité protégée.")
