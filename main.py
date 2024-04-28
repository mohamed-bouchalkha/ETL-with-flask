from flask import Flask, render_template, request
import pandas as pd
import psycopg2

app = Flask(__name__, static_folder='static', static_url_path='/static')

INDEX_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <style>
        .vh-100 {
            height: 100vh;
            width: 100%;
            background: url("https://t3.ftcdn.net/jpg/05/17/52/72/360_F_517527260_qUhb6gIyLwPcwNJhTvWCMG9uyANe1uzS.jpg"); /* Utilisez le chemin d'accès correct ici */
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }
        #simo {
            border: 2px solid rgba(60, 16, 206, 0.5);
            /* z-index: 10; */
            background-color: rgba(3, 11, 37, 0.297);
            border-radius: 20px;
            backdrop-filter: blur(120px);
        }
    </style>
</head>
<body>
<section class="vh-100" style="background-color: #ffffff; height: 100%;">
    <div class="container py-5 h-100">
        <div class="row d-flex justify-content-center align-items-center h-100">
            <div class="col col-xl-10">
                <div id="simo" class="card" style="border-radius: 1rem;">
                    <div class="row g-0">
                        <div class="col-md-6 col-lg-5 d-none d-md-block">
                            <img font-size="" src="https://miro.medium.com/v2/resize:fit:1200/1*3dtgp0e8n42ZJuD1qE4ttw.png"
                                 alt="login form" class="img-fluid" style="border-radius: 1rem 0 0 1rem; width:500px; height:100%;" />
                        </div>
                        <div class="col-md-6 col-lg-7 d-flex align-items-center">
                            <div class="card-body p-4 p-lg-5 text-black">
                                <form id="uploadForm" enctype="multipart/form-data">
                                    <div class="d-flex align-items-center mb-3 pb-1">
                                        <i class="fas fa-cubes fa-2x me-3" style="color: #ff6219;"></i>
                                    </div>
                                    <h5 class="fw-normal mb-3 pb-3" style="letter-spacing: 1px; color: red; font-family: 'Arial', sans-serif; font-size:40px;font-weiddth:40px;">Prototype d'ETL</h5>
                                    <input class="form-control form-control-lg" type="file" name="file">
                                    <div class="pt-1 mb-4">
                                        <button id="submitBtn" class="btn btn-dark btn-lg btn-block" type="button">Sauvegarder</button>
                                    </div>
                                    <a href="#!" class="small text-muted">Terms of use.</a>
                                    <a href="#!" class="small text-muted">Privacy policy</a>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<script>
    document.getElementById("submitBtn").addEventListener("click", function(){
        var form = document.getElementById("uploadForm");
        var formData = new FormData(form);
        
        fetch("/upload", {
            method: "POST",
            body: formData
        })
        .then(response => response.text())
        .then(data => {
            alert(data); // Afficher la réponse dans une boîte de dialogue d'alerte
            form.reset(); // Réinitialiser le formulaire après avoir affiché l'alerte
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });
</script>

</body>
</html>
''' 

@app.route('/')
def index():
    return INDEX_HTML

def save_to_database(df):
    conn = psycopg2.connect(database="ETL", user="postgres", password="mohamed5050#", host="localhost", port="5432")
    cursor = conn.cursor()
    
    for index, row in df.iterrows():
        cursor.execute("INSERT INTO bilan (art_id, qte_actuelle) VALUES (%s, %s)", (row['id'], row['qte_actuelle']))
    
    conn.commit()
    conn.close()

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename.endswith('.xlsx'):
            df_articles = pd.read_excel(f, 'Articles')
            df_achats = pd.read_excel(f, 'Achats')
            df_ventes = pd.read_excel(f, 'Ventes')
            
            achats_grouped = df_achats.groupby('id')['qte'].sum()
            ventes_grouped = df_ventes.groupby('id')['qte'].sum()
            
            df_articles['qte_actuelle'] = df_articles.apply(lambda row: achats_grouped.get(row['id'], 0) - ventes_grouped.get(row['id'], 0), axis=1)
            
            save_to_database(df_articles)
            
            return "Traitement terminé et enregistré dans la base de données."
        else:
            return "Le fichier doit être au format Excel (.xlsx)."

if __name__ == '__main__':
    app.run(debug=True)
