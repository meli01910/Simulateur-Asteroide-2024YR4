import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button

# Couleurs des planètes
colors = {
    "Mercure": "gray",
    "Vénus": "orange",
    "Terre": "blue",
    "Mars": "red",
    "Jupiter": "brown",
    "Saturne": "gold",
    "Uranus": "cyan",
    "Neptune": "purple",
    "2024 YR4": "white"
}

# Paramètres des planètes : [demi-grand axe (UA), excentricité, période (années)]
planets = {
    "Mercure": [0.39, 0.206, 0.24],
    "Vénus": [0.72, 0.007, 0.62],
    "Terre": [1.00, 0.017, 1.00],
    "Mars": [1.52, 0.093, 1.88],
    "Jupiter": [5.20, 0.049, 11.86],
    "Saturne": [9.58, 0.056, 29.46],
    "Uranus": [19.22, 0.046, 84.01],
    "Neptune": [30.05, 0.010, 164.79],
    "2024 YR4": [2.515865550528513, 0.6615479033633554, 4.04]
}

# Constantes
steps_per_year = 500

# Calcul des orbites
def calculate_orbits(planets, steps_per_year):
    orbits = {}
    for name, params in planets.items():
        a, e, T = params
        num_steps = int(T * steps_per_year)
        theta = np.linspace(0, 2 * np.pi, num_steps)
        r = a * (1 - e**2) / (1 + e * np.cos(theta))
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        orbits[name] = (x, y, T)
    return orbits

# Initialisation de la figure

fig, ax = plt.subplots(figsize=(10, 10)) 
plt.subplots_adjust(left=0, right=1, bottom=0, top=1)  

ax.set_aspect("equal")
ax.set_xlim(-35, 35)
ax.set_ylim(-35, 35)
ax.set_facecolor("black")
ax.set_title("Simulateur de Système Solaire", fontsize=18, color="white")
ax.set_xlabel("Distance (UA)", fontsize=14, color="white")
ax.set_ylabel("Distance (UA)", fontsize=14, color="white")
ax.grid(True, alpha=0.2)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('white')

# Calcul des orbites
orbits = calculate_orbits(planets, steps_per_year)

# Ajout des points et trajectoires
points = {}
trajectories = {}
labels = {}
visible_planets = list(planets.keys())

for name, (x, y, _) in orbits.items():
    point, = ax.plot([], [], "o", color=colors[name], markersize=8)
    trajectory, = ax.plot([], [], "-", color=colors[name], alpha=1, lw=2)
    label = ax.text(0, 0, name, fontsize=8, color=colors[name], ha='center', va='center', visible=False)
    
    points[name] = point
    trajectories[name] = trajectory
    labels[name] = label

# Légende pour les couleurs des planètes
legend_elements = []
for name, color in colors.items():
    legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                       markerfacecolor=color, markersize=8, label=name))
ax.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(1.2, 1), fontsize=10, facecolor='black', edgecolor='white', labelcolor='white')

# Soleil
sun = ax.plot(0, 0, "o", color='yellow', markersize=15)[0]
sun_label = ax.text(0, 1.5, "Soleil", fontsize=10, color='yellow', ha='center', va='center')

# Texte pour afficher le temps
time_text = ax.text(0.02, 0.95, "", fontsize=14, transform=ax.transAxes, color='white')
info_text = ax.text(0.02, 0.90, "", fontsize=12, transform=ax.transAxes, color='white')

# Variables globales pour les contrôles
paused = False
speed_factor = 1.0
show_labels = False
target_planet = None
trajectory_length = 500 

# Ajouter les contrôles sous le graphique
ax_speed = plt.axes([0.1, 0.15, 0.65, 0.03])
ax_zoom = plt.axes([0.1, 0.1, 0.65, 0.03])
ax_pause = plt.axes([0.8, 0.15, 0.1, 0.03])
ax_reset = plt.axes([0.8, 0.1, 0.1, 0.03])
ax_labels = plt.axes([0.1, 0.05, 0.3, 0.03])

# Créer les widgets
speed_slider = Slider(ax_speed, 'Vitesse', 0.1, 5.0, valinit=1.0)
zoom_slider = Slider(ax_zoom, 'Zoom', 0.1, 15.0, valinit=1.0)
pause_button = Button(ax_pause, 'Pause/Play')
reset_button = Button(ax_reset, 'Reset')
labels_check = Button(ax_labels,'Afficher les noms des planètes')

# Dictionnaire pour stocker les coordonnées des trajectoires
trajectory_x = {name: [] for name in planets}
trajectory_y = {name: [] for name in planets}

# Mise à jour des animations
# Calcul des orbites (ajusté pour tracer les orbites complètes)
def calculate_orbits(planets, steps_per_year):
    orbits = {}
    for name, params in planets.items():
        a, e, T = params
        num_steps = int(T * steps_per_year)
        theta = np.linspace(0, 2 * np.pi, num_steps)
        r = a * (1 - e**2) / (1 + e * np.cos(theta))
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        orbits[name] = (x, y, T)
    return orbits


# Fonction pour sélectionner une planète en cliquant
def on_click(event):
    global target_planet
    
    if event.inaxes != ax:
        return
    
    # Déterminer quelle planète est la plus proche du clic
    click_x, click_y = event.xdata, event.ydata
    min_dist = float('inf')
    closest_planet = None
    
    for name, planet_point in points.items():
        px, py = planet_point.get_data()
        if len(px) > 0:  # Vérifier que les données existent
            dist = np.sqrt((px[0] - click_x)**2 + (py[0] - click_y)**2)
            if dist < min_dist and dist < 3:  # Seuil de distance pour la sélection
                min_dist = dist
                closest_planet = name
    
    # Si on clique sur une planète, la cibler; sinon, désactiver le ciblage
    if closest_planet:
        target_planet = closest_planet
    else:
        target_planet = None

# Mise à jour des animations (ajuster zoom pour la planète ciblée)
def update(frame):
    global paused, target_planet, trajectory_x, trajectory_y
    
    if paused:
        return list(points.values()) + list(trajectories.values()) + [time_text, info_text, sun_label] + list(labels.values())
    
    real_frame = int(frame * speed_factor)
    simulated_years = real_frame / steps_per_year
    time_text.set_text(f"Temps simulé : {simulated_years:.2f} années")
    
    # Variables pour stocker la position de la planète cible (si sélectionnée)
    target_x, target_y = None, None
    
    for name, (x, y, _) in orbits.items():
        idx = real_frame % len(x)
        
        # Mise à jour de la position
        points[name].set_data([x[idx]], [y[idx]])
        
        # Ajouter le point actuel à l'historique de trajectoire
        trajectory_x[name].append(x[idx])
        trajectory_y[name].append(y[idx])
        
        # Limiter la longueur des trajectoires
        if len(trajectory_x[name]) > trajectory_length:
            trajectory_x[name] = trajectory_x[name][-trajectory_length:]
            trajectory_y[name] = trajectory_y[name][-trajectory_length:]
        
        # Mettre à jour la trajectoire (orbite complète ici)
        trajectories[name].set_data(x, y)  # Affichage de l'orbite complète (pas seulement les derniers points)
        
        # Étiquettes
        labels[name].set_position((x[idx], y[idx] + 1.5))
        labels[name].set_visible(show_labels)
        
        # Si c'est la planète cible, stocker sa position
        if name == target_planet:
            target_x, target_y = x[idx], y[idx]
            a, e, T = planets[name]
            distance = np.sqrt(x[idx]**2 + y[idx]**2)
            info_text.set_text(f"Planète: {name} | Distance: {distance:.2f} UA | " +
                              f"Période: {T:.2f} ans | Excentricité: {e:.3f}")
    
    # Si une planète est ciblée, ajuster la vue
    if target_planet and target_x is not None and target_y is not None:
        zoom = zoom_slider.val
        # Réduire la fenêtre pour un zoom plus précis près de la planète
        window_size = 15 / zoom  # Réduire la taille de la fenêtre pour un zoom plus intense
        ax.set_xlim(target_x - window_size, target_x + window_size)
        ax.set_ylim(target_y - window_size, target_y + window_size)
    else:
        # Sinon, vue centrée sur le Soleil avec zoom ajusté
        zoom = zoom_slider.val
        window_size = 35 / zoom
        ax.set_xlim(-35 / zoom, 35 / zoom)
        ax.set_ylim(-35 / zoom, 35 / zoom)
        info_text.set_text("")
    
    return list(points.values()) + list(trajectories.values()) + [time_text, info_text, sun_label] + list(labels.values())



# Fonctions de callback pour les contrôles
def update_speed(val):
    global speed_factor
    speed_factor = val

def update_zoom(val):
    # La mise à jour du zoom se fait dans la fonction principale update()
    pass

def toggle_pause(event):
    global paused
    paused = not paused

def reset_view(event):
    global target_planet, trajectory_x, trajectory_y
    target_planet = None
    zoom_slider.set_val(1.0)
    ax.set_xlim(-35, 35)
    ax.set_ylim(-35, 35)
    
    # Effacer toutes les trajectoires
    for name in planets:
        trajectory_x[name] = []
        trajectory_y[name] = []
        trajectories[name].set_data([], [])

def toggle_labels(label):
    global show_labels
    show_labels = not show_labels


# Connecter les callbacks
speed_slider.on_changed(update_speed)
zoom_slider.on_changed(update_zoom)
pause_button.on_clicked(toggle_pause)
reset_button.on_clicked(reset_view)
labels_check.on_clicked(toggle_labels)
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('scroll_event', lambda event: zoom_slider.set_val(
    min(15.0, max(0.1, zoom_slider.val * (1.1 if event.button == 'up' else 0.9)))
))

# Animation
ani = FuncAnimation(fig, update, frames=steps_per_year * 10, interval=20, blit=True)

plt.show()
