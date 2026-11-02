# Vision Main — suivi de la main en temps réel

🇫🇷 [Français](#français) · 🇬🇧 [English](#english)

![Démo](images/demo.png)

---

## Français

### Ce que fait le projet
Le script ouvre la webcam, repère les mains avec **MediaPipe Hands** et dessine leur squelette (21 points et leurs liaisons) en direct.
Un bouton **QUITTER** affiché sur l'image s'utilise sans clavier : il suffit d'y poser le bout de l'index.

### Ce que j'ai ajouté par rapport à l'exemple officiel
Le script part de l'exemple officiel MediaPipe Hands en Python :
[google-ai-edge/mediapipe — docs/solutions/hands.md](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/hands.md).
Par rapport à cet exemple, j'ai ajouté :
- un **bouton virtuel QUITTER**, qui s'active quand le bout de l'index (repère 8) entre dans le rectangle ;
- un **retour visuel** : le bouton passe du rouge au vert quand l'index le survole ;
- un **clic souris** sur le bouton (`cv2.setMouseCallback`) ;
- un **bouton placé selon la taille de l'image** (`frame.shape`), quelle que soit la résolution de la webcam ;
- un **arrêt réel quand on ferme la fenêtre** avec la croix (`cv2.getWindowProperty`) ;
- un **message clair** si la webcam ne s'ouvre pas ;
- l'**affichage des images par seconde** (FPS) ;
- une **sortie propre** : la webcam et le modèle sont libérés (`cap.release()`, `hands.close()`).

### Installation
Python 3.9 à 3.12 (`mediapipe` 0.10.21 n'existe pas pour Python 3.13).

```bash
git clone https://github.com/Valentin-Auger-Laboratoire/vision-main.git
cd vision-main
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

La version de `mediapipe` est fixée à 0.10.21, car le script utilise l'API `mp.solutions`. Celle-ci n'existe plus dans les versions récentes.

### Lancement
```bash
python app.py
```

### Contrôles
| Action | Effet |
|---|---|
| Touche **Q** | Quitter |
| **Croix** de la fenêtre | Quitter |
| **Bout de l'index** sur le bouton QUITTER | Quitter (le bouton passe au vert) |
| **Clic gauche** sur le bouton QUITTER | Quitter |

### Capture d'écran
Place une capture dans `images/demo.png` : elle s'affiche en haut de cette page.

---

## English

### What it does
The script opens the webcam, detects hands with **MediaPipe Hands** and draws their skeleton (21 landmarks and their connections) in real time.
A **QUITTER** (quit) button drawn on the frame works without a keyboard: just point your index fingertip at it.

### What I added to the official example
The script starts from the official MediaPipe Hands Python example:
[google-ai-edge/mediapipe — docs/solutions/hands.md](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/hands.md).
On top of that example, I added:
- a **virtual QUIT button** that fires when the index fingertip (landmark 8) enters the rectangle;
- **visual feedback**: the button turns from red to green when the fingertip is over it;
- a **mouse click** on the button (`cv2.setMouseCallback`);
- a **button positioned from the frame size** (`frame.shape`), whatever the webcam resolution;
- a **real exit when the window is closed** with the X (`cv2.getWindowProperty`);
- a **clear error message** if the webcam can't be opened;
- an **on-screen FPS counter**;
- a **clean shutdown** that releases the webcam and the model (`cap.release()`, `hands.close()`).

### Installation
Python 3.9 to 3.12 (`mediapipe` 0.10.21 is not available for Python 3.13).

```bash
git clone https://github.com/Valentin-Auger-Laboratoire/vision-main.git
cd vision-main
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

`mediapipe` is pinned to 0.10.21 because the script uses the `mp.solutions` API, which is gone from recent releases.

### Run
```bash
python app.py
```

### Controls
| Action | Effect |
|---|---|
| **Q** key | Quit |
| Window **X** button | Quit |
| **Index fingertip** on the QUITTER button | Quit (the button turns green) |
| **Left click** on the QUITTER button | Quit |

### Screenshot
Put a screenshot in `images/demo.png`: it shows at the top of this page.
