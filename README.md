# Vision Main — interactions gestuelles avec la webcam

🇫🇷 [Français](#français) · 🇬🇧 [English](#english)

---

## Français

### Ce que contient le dépôt
Une série en deux étapes, construite sur **MediaPipe Hands** et **OpenCV** :

| Étape | Script | Ce qu'il fait |
|---|---|---|
| 1 | `app.py` | Suivi de la main en temps réel et bouton **QUITTER** activé au doigt |
| 2 | `construction_gestes.py` | Construction de cubes : **pince** pour poser, **grille aimantée**, **profondeur estimée** par la taille de la main, effacement |

Les deux scripts partent de l'exemple officiel MediaPipe Hands en Python :
[google-ai-edge/mediapipe — docs/solutions/hands.md](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/hands.md).

### Étape 1 — `app.py` : suivi de la main
Le script ouvre la webcam, repère les mains et dessine leur squelette (21 points et leurs liaisons) en direct.
Un bouton **QUITTER** affiché sur l'image s'utilise sans clavier : il suffit d'y poser le bout de l'index.

Par rapport à l'exemple officiel, j'ai ajouté :
- un **bouton virtuel QUITTER**, qui s'active quand le bout de l'index (repère 8) entre dans le rectangle ;
- un **retour visuel** : le bouton passe du rouge au vert quand l'index le survole ;
- un **clic souris** sur le bouton (`cv2.setMouseCallback`) ;
- un **bouton placé selon la taille de l'image** (`frame.shape`), quelle que soit la résolution de la webcam ;
- un **arrêt réel quand on ferme la fenêtre** avec la croix (`cv2.getWindowProperty`) ;
- un **message clair** si la webcam ne s'ouvre pas ;
- l'**affichage des images par seconde** (FPS) ;
- une **sortie propre** : la webcam et le modèle sont libérés (`cap.release()`, `hands.close()`).

| Action | Effet |
|---|---|
| Touche **Q** | Quitter |
| **Croix** de la fenêtre | Quitter |
| **Bout de l'index** sur le bouton QUITTER | Quitter (le bouton passe au vert) |
| **Clic gauche** sur le bouton QUITTER | Quitter |

### Étape 2 — `construction_gestes.py` : construire des cubes à la main
Un cube fantôme (bleu ciel) suit le bout de l'index. On le pose en pinçant le pouce et l'index, et il se fige en vert.

- **Grille aimantée** : la position est arrondie sur une grille dont le pas dépend de la largeur de l'image.
- **Profondeur simulée** : l'écart entre le poignet et la base de l'index grandit quand la main se rapproche de la caméra. Il fixe la taille du cube : plus la main est proche, plus le cube est grand. **Ce n'est pas de la vraie 3D** : aucune profondeur n'est mesurée, et les cubes sont dessinés en perspective (face avant, face arrière décalée, arêtes reliées) sur l'image 2D.
- **Deux mains** : chaque main a son propre verrou, donc une pince pose exactement un cube.
- **Effacement** : poing fermé ou touche Z pour retirer le dernier cube, touche C pour tout effacer.
- **Proportions** : le seuil de pince, le pas de la grille, la taille des cubes et le bouton OFF s'adaptent à la résolution de la webcam.
- Affichage du **nombre de cubes** et des **FPS**, message clair si la webcam ne s'ouvre pas, sortie propre.

| Action | Effet |
|---|---|
| **Pince** pouce + index | Poser un cube |
| **Rapprocher / éloigner** la main | Agrandir / réduire le cube fantôme |
| **Poing fermé** | Effacer le dernier cube |
| Touche **Z** | Effacer le dernier cube |
| Touche **C** | Tout effacer |
| Touche **Q** | Quitter |
| **Croix** de la fenêtre | Quitter |
| **Clic gauche** sur le bouton OFF | Quitter |

### Installation (commune aux deux scripts)
Python 3.9 à 3.12 (`mediapipe` 0.10.21 n'existe pas pour Python 3.13).

```bash
git clone https://github.com/Valentin-Auger-Laboratoire/vision-main.git
cd vision-main
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

La version de `mediapipe` est fixée à 0.10.21, car les scripts utilisent l'API `mp.solutions`. Celle-ci n'existe plus dans les versions récentes.

### Lancement
```bash
python app.py                  # Étape 1
python construction_gestes.py  # Étape 2
```

---

## English

### What's in the repository
A two-step series built on **MediaPipe Hands** and **OpenCV**:

| Step | Script | What it does |
|---|---|---|
| 1 | `app.py` | Real-time hand tracking and a **QUITTER** (quit) button pressed with a fingertip |
| 2 | `construction_gestes.py` | Cube building: **pinch** to place, **snap-to-grid**, **depth estimated** from hand size, undo |

Both scripts start from the official MediaPipe Hands Python example:
[google-ai-edge/mediapipe — docs/solutions/hands.md](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/hands.md).

### Step 1 — `app.py`: hand tracking
The script opens the webcam, detects hands and draws their skeleton (21 landmarks and their connections) in real time.
A **QUITTER** button drawn on the frame works without a keyboard: just point your index fingertip at it.

On top of the official example, I added:
- a **virtual QUIT button** that fires when the index fingertip (landmark 8) enters the rectangle;
- **visual feedback**: the button turns from red to green when the fingertip is over it;
- a **mouse click** on the button (`cv2.setMouseCallback`);
- a **button positioned from the frame size** (`frame.shape`), whatever the webcam resolution;
- a **real exit when the window is closed** with the X (`cv2.getWindowProperty`);
- a **clear error message** if the webcam can't be opened;
- an **on-screen FPS counter**;
- a **clean shutdown** that releases the webcam and the model (`cap.release()`, `hands.close()`).

| Action | Effect |
|---|---|
| **Q** key | Quit |
| Window **X** button | Quit |
| **Index fingertip** on the QUITTER button | Quit (the button turns green) |
| **Left click** on the QUITTER button | Quit |

### Step 2 — `construction_gestes.py`: building cubes by hand
A ghost cube (light blue) follows the index fingertip. Pinch your thumb and index finger to place it, and it freezes in green.

- **Snap-to-grid**: the position is rounded to a grid whose step depends on the frame width.
- **Simulated depth**: the distance between the wrist and the base of the index finger grows as the hand gets closer to the camera. It sets the cube size: the closer the hand, the bigger the cube. **This is not real 3D**: no depth is measured, and the cubes are drawn in perspective (front face, offset back face, connected edges) on the 2D image.
- **Two hands**: each hand has its own lock, so one pinch places exactly one cube.
- **Undo**: a closed fist or the Z key removes the last cube, and the C key clears everything.
- **Proportions**: the pinch threshold, grid step, cube size and OFF button scale with the webcam resolution.
- On-screen **cube count** and **FPS**, a clear message if the webcam can't be opened, and a clean shutdown.

| Action | Effect |
|---|---|
| Thumb + index **pinch** | Place a cube |
| Move the hand **closer / farther** | Enlarge / shrink the ghost cube |
| **Closed fist** | Remove the last cube |
| **Z** key | Remove the last cube |
| **C** key | Clear everything |
| **Q** key | Quit |
| Window **X** button | Quit |
| **Left click** on the OFF button | Quit |

### Installation (shared by both scripts)
Python 3.9 to 3.12 (`mediapipe` 0.10.21 is not available for Python 3.13).

```bash
git clone https://github.com/Valentin-Auger-Laboratoire/vision-main.git
cd vision-main
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

`mediapipe` is pinned to 0.10.21 because the scripts use the `mp.solutions` API, which is gone from recent releases.

### Run
```bash
python app.py                  # Step 1
python construction_gestes.py  # Step 2
```
