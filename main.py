from flask import Flask, render_template, request, g, redirect, url_for, session
from simulator import Character, Artifact, Type, Stat, trial_genetic, get_damage_flat, get_damage_aggravate
import pickle


app = Flask(__name__)
app.secret_key = 'KEY'
global_session = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/simulator', methods=['GET', 'POST'])
def simulate():
    if request.method == 'POST':
        stats = {Stat.ATK: float(request.form['ATK']), Stat.CR: float(request.form['CR']),\
                Stat.CD: float(request.form['CD']), Stat.DEF: float(request.form['DEF']),\
                Stat.HP: float(request.form['HP'])}

        f = get_damage_flat
        match request.form['FUNC']:
            case 'aggravate': f = get_damage_aggravate

        char = Character(stats)
        char = trial_genetic(int(request.form['N']), dmg_func = f, god = char)

        global_session['c'] = char
        global_session['f'] = f

        return redirect(url_for('results'))
        
    else:
        return render_template('simulate.html')


@app.route('/results', methods = ['GET', 'POST'])
def results():
    if request.method == 'POST':

        with open('./artifacts/a1', 'ab') as f:
            f.write(pickle.dumps(global_session['c']))

        global_session.pop('c', 'key not found')
        global_session.pop('f', 'key not found')

        return redirect(url_for('simulate'))

    else:
        return render_template('results.html', c = global_session['c'], function = global_session['f'])


@app.route('/characters', methods = ['GET', 'POST'])
def characters():
    return render_template('characters.html')


@app.route('/artifacts', methods = ['GET', 'POST'])
def artifacts():
    with open('./artifacts/a1', 'rb') as f:
        c = pickle.load(f)

    return render_template('artifacts.html', c = c)

@app.route('/create_artifact', methods = ['GET', 'POST'])
def create_artifact():
    if request.method == "POST":
        pass
    else:
        return render_template('create_artifact.html')
