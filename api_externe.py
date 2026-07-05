import csv
import math
import os
from flask import Flask, jsonify, request

DATA_DIR = os.environ.get("DATA_DIR", "./data_recouvrement")

TABLES = [
    "clients",
    "factures",
    "paiements",
    "contrats",
    "impayes",
    "relances",
    "dossiers_recouvrement",
    "litiges",
    "suspensions_ligne",
    "echeanciers",
    "mouvements_financiers",
]

app = Flask(__name__)


@app.route("/api/health")
def health():
    return jsonify({"statut": "OK"})


@app.route("/api/tables")
def list_tables():
    return jsonify({"tables": TABLES})


@app.route("/api/data/<table>")
def get_table(table):
    if table not in TABLES:
        return jsonify({"erreur": f"Table inconnue : {table}. Tables disponibles : {TABLES}"}), 404

    csv_path = os.path.join(DATA_DIR, f"{table}.csv")
    if not os.path.isfile(csv_path):
        return jsonify({"erreur": f"Fichier introuvable : {csv_path}"}), 404

    try:
        page   = max(1, int(request.args.get("page",   1)))
        limite = max(1, int(request.args.get("limite", 10000)))
    except ValueError:
        return jsonify({"erreur": "Les paramètres 'page' et 'limite' doivent être des entiers."}), 400

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader      = csv.DictReader(f)
        debut       = (page - 1) * limite
        toutes      = []
        total_lignes = 0
        for i, ligne in enumerate(reader):
            total_lignes += 1
            if debut <= i < debut + limite:
                toutes.append(ligne)

    total_pages = math.ceil(total_lignes / limite) if limite else 1

    return jsonify({
        "table":          table,
        "page":           page,
        "limite":         limite,
        "total_lignes":   total_lignes,
        "total_pages":    total_pages,
        "a_page_suivante": page < total_pages,
        "nombre_lignes":  len(toutes),
        "donnees":        toutes,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5030)
