from pulp import *


medecins = {
    "Dr Youssef": {"Pédiatrie": True},
    "Dr Khadija": {"Pédiatrie": True},
    "Dr Omar": {"Pédiatrie": True, "Urgences": True},
    "Dr Salma": {"Urgences": True, "Néonatologie": True},
    "Dr Rachid": {"Consultations": True, "Maternité": True},
    "Dr Nisrine": {"Exploration": True},
    "Dr Anas": {"Urgences": True, "Consultations": True, "Astreinte": True},
    "Dr Fatima": {"Exploration": True, "Astreinte": True, "Maternité": True, "Néonatologie": True},
    "Dr Hicham": {"Maternité": True, "Néonatologie": True}
}

vacances = {
    "Dr Anas": ["Lundi-AM", "Lundi-PM", "Lundi-GA", "Mardi-AM", "Mardi-PM", "Mardi-GA",
               "Mercredi-AM", "Mercredi-PM", "Mercredi-GA", "Jeudi-AM", "Jeudi-PM", "Jeudi-GA",
               "Vendredi-AM", "Vendredi-PM", "Vendredi-GA", "Samedi-AM", "Samedi-PM", "Samedi-GA",
               "Dimanche-AM", "Dimanche-PM", "Dimanche-GA"]
}

besoins = {
    "Pédiatrie": {
        "Lundi-AM": 2, "Lundi-PM": 1,
        "Mardi-AM": 2, "Mardi-PM": 1,
        "Mercredi-AM": 2, "Mercredi-PM": 1,
        "Jeudi-AM": 2, "Jeudi-PM": 1,
        "Vendredi-AM": 2, "Vendredi-PM": 1
    },
    "Urgences": {
        "Lundi-AM": 1, "Lundi-PM": 1, "Lundi-GA": 1,
        "Mardi-AM": 1, "Mardi-PM": 1, "Mardi-GA": 1,
        "Mercredi-AM": 1, "Mercredi-PM": 1, "Mercredi-GA": 1,
        "Jeudi-AM": 1, "Jeudi-PM": 1, "Jeudi-GA": 1,
        "Vendredi-AM": 1, "Vendredi-PM": 1, "Vendredi-GA": 1,
        "Samedi-AM": 1, "Samedi-PM": 1, "Samedi-GA": 1,
        "Dimanche-AM": 1, "Dimanche-PM": 1, "Dimanche-GA": 1
    },
    "Consultations": {
        "Lundi-PM": 1, "Mardi-PM": 1, "Mercredi-PM": 1, "Jeudi-PM": 1, "Vendredi-PM": 1
    },
    "Exploration": {
        "Mercredi-AM": 1
    },
    "Astreinte": {
        "Lundi-GA": 1, "Mardi-GA": 1, "Mercredi-GA": 1, "Jeudi-GA": 1, "Vendredi-GA": 1,
        "Samedi-GA": 1, "Dimanche-GA": 1
    },
    "Maternité": {
        "Lundi-AM": 1, "Mardi-AM": 1, "Mercredi-AM": 1, "Jeudi-AM": 1, "Vendredi-AM": 1
    },
    "Néonatologie": {
        "Lundi-AM": 1, "Lundi-PM": 1, "Lundi-GA": 1,
        "Mardi-AM": 1, "Mardi-PM": 1, "Mardi-GA": 1,
        "Mercredi-AM": 1, "Mercredi-PM": 1, "Mercredi-GA": 1,
        "Jeudi-AM": 1, "Jeudi-PM": 1, "Jeudi-GA": 1,
        "Vendredi-AM": 1, "Vendredi-PM": 1, "Vendredi-GA": 1,
        "Samedi-AM": 1, "Samedi-PM": 1, "Samedi-GA": 1,
        "Dimanche-AM": 1, "Dimanche-PM": 1, "Dimanche-GA": 1
    }
}

# Initialisation du problème
prob = LpProblem("Planification_Hopital", LpMinimize)

# Création des variables
variables_x = {}
variables_y = {}
variables_z = {}
variables_h = {}

# 1. Variables d'affectation (x)
for med in medecins:
    for act in medecins[med]:
        for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]:
            for creneau in ["AM", "PM", "GA"]:
                cle = (med, act, jour, creneau)
                variables_x[cle] = LpVariable(f"x_{med}_{act}_{jour}_{creneau}", cat="Binary")

# 2. Variables de remplaçants (y)
for act in besoins:
    for jour_creneau in besoins[act]:
        jour, creneau = jour_creneau.split("-")
        variables_y[(act, jour, creneau)] = LpVariable(f"y_{act}_{jour}_{creneau}", lowBound=0, cat="Integer")

# 3. Variables de stabilité (z)
for med in medecins:
    for act in medecins[med]:
        for i in range(1, 7):  # Pour les jours du mardi au dimanche (stabilité avec jour précédent)
            jour = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][i]
            jour_prev = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][i-1]
            for creneau in ["AM", "PM", "GA"]:
                variables_z[(med, act, jour, creneau)] = LpVariable(f"z_{med}_{act}_{jour}_{creneau}", cat="Binary")

# 4. Variables de charge (h)
for med in medecins:
    variables_h[med] = LpVariable(f"h_{med}", lowBound=0)

# Contraintes
# 1. Couverture des besoins
for act in besoins:
    for jour_creneau in besoins[act]:
        jour, creneau = jour_creneau.split("-")
        medecins_competents = [med for med in medecins if medecins[med].get(act, False)]
        prob += lpSum(variables_x[(med, act, jour, creneau)] for med in medecins_competents) + \
                variables_y[(act, jour, creneau)] >= besoins[act][jour_creneau]

# 2. Indisponibilités (vacances)
for med in vacances:
    for jour_creneau in vacances[med]:
        jour, creneau = jour_creneau.split("-")
        for act in medecins[med]:
            prob += variables_x[(med, act, jour, creneau)] == 0

# 3. Charge maximale (10 demi-journées)
for med in medecins:
    prob += variables_h[med] == lpSum(variables_x[(med, act, jour, creneau)] 
                                  for act in medecins[med]
                                  for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
                                  for creneau in ["AM", "PM", "GA"])
    prob += variables_h[med] <= 10

# 4. Stabilité du planning
for med in medecins:
    for act in medecins[med]:
        for i in range(1, 7):
            jour = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][i]
            jour_prev = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][i-1]
            for creneau in ["AM", "PM", "GA"]:
                prob += variables_z[(med, act, jour, creneau)] <= variables_x[(med, act, jour, creneau)]
                prob += variables_z[(med, act, jour, creneau)] <= variables_x[(med, act, jour_prev, creneau)]
                prob += variables_z[(med, act, jour, creneau)] >= variables_x[(med, act, jour, creneau)] + \
                                                               variables_x[(med, act, jour_prev, creneau)] - 1

# 5. Un seul créneau par jour²
for med in medecins:
    for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]:
        prob += lpSum(variables_x[(med, act, jour, creneau)] 
                     for act in medecins[med]
                     for creneau in ["AM", "PM", "GA"]) <= 1

# 6. Repos après garde de nuit
for med in medecins:
    if medecins[med].get("Astreinte", False):
        for i in range(7):
            jour = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][i]
            jour_suiv = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][(i + 1) % 7]
            prob += variables_x[(med, "Astreinte", jour, "GA")] + \
                   lpSum(variables_x[(med, act, jour_suiv, creneau)]
                        for act in medecins[med]
                        for creneau in ["AM", "PM", "GA"]) <= 1

# Fonction objectif
alpha = {"Urgences": 100, "Néonatologie": 100, "Pédiatrie": 50, 
         "Astreinte": 80, "Maternité": 70, "Consultations": 10, "Exploration": 30}
beta = 1
gamma = 5

# Termes de la fonction objectif
term_remplacants = lpSum(alpha[act] * variables_y[(act, jour, creneau)]
                        for act in besoins
                        for jour_creneau in besoins[act]
                        for jour, creneau in [jour_creneau.split("-")])

charge_max = LpVariable("charge_max", lowBound=0)
charge_min = LpVariable("charge_min", lowBound=0)
for med in medecins:
    prob += variables_h[med] <= charge_max
    prob += variables_h[med] >= charge_min

# PuLP traite des expressions lineaires : on minimise l'ecart max-min
# plutot qu'un terme quadratique non supporte par le solveur MILP.
term_equite = charge_max - charge_min

term_stabilite = lpSum(variables_x[(med, act, jour, creneau)] - variables_z[(med, act, jour, creneau)]
                      for med in medecins
                      for act in medecins[med]
                      for i in range(1, 7)
                      for jour, creneau in [(["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][i], c) 
                                          for c in ["AM", "PM", "GA"]])

prob += term_remplacants + beta * term_equite + gamma * term_stabilite

# Résolution
prob.solve(PULP_CBC_CMD(msg=False))

# Affichage des résultats
print("Statut:", LpStatus[prob.status])
print("Valeur optimale:", value(prob.objective))

print("\nAffectations:")
for med in medecins:
    print(f"\n{med}:")
    for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]:
        for creneau in ["AM", "PM", "GA"]:
            for act in medecins[med]:
                if value(variables_x.get((med, act, jour, creneau), 0)) > 0.5:
                    print(f"  {jour}-{creneau}: {act}")

print("\nRemplaçants nécessaires:")
for act in besoins:
    for jour_creneau in besoins[act]:
        jour, creneau = jour_creneau.split("-")
        if value(variables_y.get((act, jour, creneau), 0)) > 0.5:
            print(f"  {act} {jour}-{creneau}: {value(variables_y[(act, jour, creneau)])}")

print("\nCharge hebdomadaire:")
for med in medecins:
    print(f"  {med}: {value(variables_h[med])} demi-journées")
      