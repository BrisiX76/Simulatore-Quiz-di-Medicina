from flask import Flask, render_template, request, redirect, session
import json, random, os

app = Flask(__name__)
app.secret_key = "test123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "domande.json"), "r", encoding="utf-8") as f:
    domande_db = json.load(f)

def genera_domande(materia, livello):
    pool = domande_db.get(materia, {}).get(livello, [])
    return random.sample(pool, min(10, len(pool)))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    materia = request.form.get("materia", "biologia")
    livello = request.form.get("livello", "medio")
    session["domande"]   = genera_domande(materia, livello)
    session["indice"]    = 0
    session["punteggio"] = 0
    session["feedback"]  = None
    session["materia"]   = materia
    session["livello"]   = livello
    return redirect("/quiz")

@app.route("/quiz", methods=["GET", "POST"])
def quiz_page():
    if "indice" not in session or "domande" not in session:
        return redirect("/")

    if request.method == "POST":
        action = request.form.get("action")

        if action == "risposta":
            scelta       = int(request.form["scelta"])
            domanda      = session["domande"][session["indice"]]
            corretta     = domanda["corretta"]
            scelta_testo = domanda["opzioni"][scelta]
            esatta       = scelta_testo == corretta

            if esatta:
                session["punteggio"] += 1

            session["feedback"] = {
                "scelta":          scelta,
                "corretta":        esatta,
                "risposta_giusta": corretta,
                "spiegazione":     domanda.get("spiegazione", "")
            }
            session.modified = True
            return redirect("/quiz")

        elif action == "avanti":
            session["indice"]  += 1
            session["feedback"] = None
            session.modified = True
            return redirect("/quiz")

    if session["indice"] >= len(session["domande"]):
        return redirect("/risultato")

    domanda  = session["domande"][session["indice"]]
    feedback = session.get("feedback")
    totale   = len(session["domande"])

    return render_template(
        "quiz.html",
        domanda  = domanda,
        indice   = session["indice"] + 1,
        totale   = totale,
        feedback = feedback,
        lettere  = ["A", "B", "C", "D"]
    )

@app.route("/start-same")
def start_same():
    materia = session.get("materia", "biologia")
    livello = session.get("livello", "medio")
    session["domande"]   = genera_domande(materia, livello)
    session["indice"]    = 0
    session["punteggio"] = 0
    session["feedback"]  = None
    session.modified = True
    return redirect("/quiz")

@app.route("/risultato")
def risultato():
    if "domande" not in session:
        return redirect("/")
    totale      = len(session.get("domande", []))
    punteggio   = session.get("punteggio", 0)
    percentuale = round((punteggio / totale) * 100) if totale else 0
    materia     = session.get("materia", "")
    livello     = session.get("livello", "")
    return render_template(
        "risultato.html",
        punteggio   = punteggio,
        totale      = totale,
        percentuale = percentuale,
        materia     = materia,
        livello     = livello
    )
@app.route("/statistiche")
def statistiche():
    return render_template("statistiche.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)