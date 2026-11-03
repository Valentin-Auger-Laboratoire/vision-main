import math
import sys
import time

import cv2
import mediapipe as mp

WINDOW_NAME = "Construction gestuelle"

# Repères MediaPipe utilisés
WRIST, THUMB_TIP, INDEX_MCP, INDEX_TIP = 0, 4, 5, 8
FINGER_TIPS = (8, 12, 16, 20)   # Bouts de l'index, du majeur, de l'annulaire, de l'auriculaire
FINGER_PIPS = (6, 10, 14, 18)   # Articulations du milieu de ces mêmes doigts

# Proportions par rapport à la largeur de l'image (indépendant de la résolution)
GRID_RATIO = 1 / 32       # Pas de la grille aimantée
PINCH_RATIO = 0.047       # Distance pouce-index sous laquelle on considère une pince
SIZE_RATIO = 0.78         # Taille du cube = écart poignet-index (normalisé) x largeur x ce ratio
MIN_SIZE_RATIO, MAX_SIZE_RATIO = 0.03, 0.30
DEPTH_RATIO = 0.35        # Décalage de la face arrière par rapport à la taille du cube

# Couleurs (BGR)
COLOR_FIXED = (0, 255, 0)      # Cubes posés
COLOR_GHOST = (255, 255, 0)    # Cube fantôme qui suit l'index
COLOR_FIST = (0, 165, 255)     # Main fermée (effacement)
COLOR_OFF = (0, 0, 255)
COLOR_TEXT = (255, 255, 255)

# Initialisation
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5)
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

cubes = []         # Liste des cubes posés : (x, y, taille)
pinch_lock = {}    # Par main : True tant que la pince n'a pas été relâchée
fist_lock = {}     # Par main : True tant que le poing n'a pas été rouvert


def button_rect(frame):
    """Bouton OFF centré en bas de l'image, dimensionné d'après la taille de l'image."""
    h, w = frame.shape[:2]
    bw, bh = int(w * 0.16), int(h * 0.09)
    x1 = (w - bw) // 2
    y1 = h - bh - int(h * 0.06)
    return x1, y1, x1 + bw, y1 + bh


def inside(x, y, rect):
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2


def on_mouse(event, x, y, flags, param):
    # Clic gauche sur le bouton = demande d'arrêt
    if event == cv2.EVENT_LBUTTONDOWN and inside(x, y, state["button"]):
        state["quit"] = True


def draw_cube(frame, x, y, size, color, thickness=2):
    """Cube en perspective : face avant, face arrière décalée selon la taille, arêtes reliées."""
    d = int(size * DEPTH_RATIO)
    front = [(x, y), (x + size, y), (x + size, y + size), (x, y + size)]
    back = [(px + d, py - d) for px, py in front]
    for i in range(4):
        cv2.line(frame, back[i], back[(i + 1) % 4], color, 1)
        cv2.line(frame, front[i], back[i], color, 1)
    for i in range(4):
        cv2.line(frame, front[i], front[(i + 1) % 4], color, thickness)


def is_fist(lms):
    """Poing fermé : chaque bout de doigt est plus près du poignet que son articulation."""
    wrist = lms[WRIST]
    for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
        d_tip = math.hypot(lms[tip].x - wrist.x, lms[tip].y - wrist.y)
        d_pip = math.hypot(lms[pip].x - wrist.x, lms[pip].y - wrist.y)
        if d_tip >= d_pip:
            return False
    return True


def put_centered(frame, text, rect, scale, color, thickness):
    x1, y1, x2, y2 = rect
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    cv2.putText(frame, text, ((x1 + x2 - tw) // 2, (y1 + y2 + th) // 2),
                cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)


cv2.namedWindow(WINDOW_NAME)
cv2.setMouseCallback(WINDOW_NAME, on_mouse)

print("Système en ligne. Pince pouce-index : poser un cube. Poing fermé ou touche 'Z' : "
      "effacer le dernier cube. Touche 'C' : tout effacer.")
print("Pour quitter : touche 'Q', croix de la fenêtre ou clic sur OFF.")

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

        grid = max(int(w * GRID_RATIO), 1)
        pinch_threshold = w * PINCH_RATIO
        min_size, max_size = int(w * MIN_SIZE_RATIO), int(w * MAX_SIZE_RATIO)
        state["button"] = button_rect(frame)

        # --- CUBES DÉJÀ POSÉS (dans l'ordre de pose) ---
        for cx, cy, cs in cubes:
            draw_cube(frame, cx, cy, cs, COLOR_FIXED)

        seen_hands = set()
        if results.multi_hand_landmarks:
            for hand_lms, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_id = handedness.classification[0].label   # "Left" ou "Right"
                seen_hands.add(hand_id)
                lms = hand_lms.landmark

                mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS,
                    mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
                    mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2))

                # --- POING FERMÉ : EFFACER LE DERNIER CUBE (un par fermeture) ---
                if is_fist(lms):
                    if not fist_lock.get(hand_id) and cubes:
                        cubes.pop()
                    fist_lock[hand_id] = True
                    wx, wy = int(lms[WRIST].x * w), int(lms[WRIST].y * h)
                    cv2.putText(frame, "EFFACER", (wx - 40, wy + 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_FIST, 2)
                    continue
                fist_lock[hand_id] = False

                # --- PROFONDEUR SIMULÉE ---
                # L'écart poignet - base de l'index grandit quand la main se rapproche de la caméra
                depth_factor = math.hypot(lms[INDEX_MCP].x - lms[WRIST].x,
                                          lms[INDEX_MCP].y - lms[WRIST].y)
                size = min(max(int(depth_factor * w * SIZE_RATIO), min_size), max_size)

                # --- POSITION AIMANTÉE SUR LA GRILLE ---
                ix, iy = int(lms[INDEX_TIP].x * w), int(lms[INDEX_TIP].y * h)
                gx, gy = (ix // grid) * grid, (iy // grid) * grid
                draw_cube(frame, gx, gy, size, COLOR_GHOST)

                # --- PINCE : POSER UN CUBE (une pose par pince et par main) ---
                tx, ty = int(lms[THUMB_TIP].x * w), int(lms[THUMB_TIP].y * h)
                if math.hypot(ix - tx, iy - ty) < pinch_threshold:
                    if not pinch_lock.get(hand_id):
                        cubes.append((gx, gy, size))
                    pinch_lock[hand_id] = True
                else:
                    pinch_lock[hand_id] = False

        # Une main qui sort de l'image retrouve ses verrous ouverts
        for hand_id in set(pinch_lock) | set(fist_lock):
            if hand_id not in seen_hands:
                pinch_lock[hand_id] = fist_lock[hand_id] = False

        # --- BOUTON OFF ---
        cv2.rectangle(frame, state["button"][:2], state["button"][2:], COLOR_OFF, cv2.FILLED)
        put_centered(frame, "OFF", state["button"], 0.9, COLOR_TEXT, 2)

        # --- NOMBRE DE CUBES ET IMAGES PAR SECONDE (moyenne lissée) ---
        now = time.perf_counter()
        instant_fps = 1.0 / max(now - prev_time, 1e-6)
        fps = instant_fps if fps == 0.0 else 0.9 * fps + 0.1 * instant_fps
        prev_time = now
        cv2.putText(frame, f"Cubes : {len(cubes)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_FIXED, 2)
        cv2.putText(frame, f"FPS : {fps:.0f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_FIXED, 2)
        cv2.putText(frame, "Z : annuler   C : tout effacer   Q : quitter", (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT, 1)

        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), ord('Q')):
            print("\n--- ARRÊT DEMANDÉ (touche Q) ---")
            break
        if key in (ord('z'), ord('Z')) and cubes:
            cubes.pop()
        if key in (ord('c'), ord('C')):
            cubes.clear()

        if state["quit"]:
            print("\n--- ARRÊT DEMANDÉ (clic sur OFF) ---")
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
