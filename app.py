#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sqlite3
import random
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super_secret_quiz_key'
DATABASE = 'quiz.db'

# Define your application password here
APP_PASSWORD = 'TCA-gluco'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        # Create questions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                option1 TEXT NOT NULL,
                option2 TEXT NOT NULL,
                option3 TEXT NOT NULL,
                option4 TEXT NOT NULL,
                correct INTEGER NOT NULL,
                image_url TEXT
            )
        ''')
        
        # NEW: Create scores table to save student submissions
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor = conn.execute('SELECT COUNT(*) FROM questions')
        if cursor.fetchone()[0] == 0:
            seed_questions = [
                # TCA Cycle

                ("The first reaction of the tricarboxylic acid cycle condenses the acetyl group of acetyl-CoA with which of the following TCA cycle intermediates?", "oxaloacetate", "malate", "citrate", "pyruvate", 0, None),
                ("Which of the following statements about the citric acid cycle is CORRECT?", "The formation of citrate from acetyl CoA and oxaloacetate is catalyzed by an irreversible reaction", "The citric acid cycle is functioning at its fastest rate when energy-rich intermediates like ATP and NADH are at their highest concentrations", "Carbon dioxide is formed at the steps catalyzed by malate dehydrogenase and by succinate dehydrogenase", "The citric acid cycle provides over 90% of the ATP requirement for erythrocytes", 0, None),
                ("The TCA cycle may operate in both catabolic and anabolic modes concurrently. Of the following reactions, which is an anaplerotic reaction of the TCA cycle?", "Pyruvate -> oxaloacetate", "Acetyl-CoA + oxaloacetate -> citrate", "Oxaloacetate -> phosphoenol pyruvate", "Oxaloacetate -> aspartate", 0, None),
                ("Which of the following TCA cycle reactions is productive of CO2?", "α-ketoglutarate -> succinyl-CoA", "Malate -> oxaloacetate", "Succinate -> fumarate", "Oxaloacetate -> citrate", 0, None),
                ("For each turn (cycle) of the TCA cycle, how many molecules of ATP equivalents are produced?", "12", "24", "18", "6", 0, None),
                ("How many rate-limiting (regulatory) steps are there in the TCA cycle?", "Three", "One", "Two", "Four", 0, None),
                ("In the TCA cycle, GTP is produced from GDP and Pi by which of the following mechanisms?", "Substrate level phosphorylation", "Oxidative phosphorylation", "Reverse phosphorylation", "cAMP-dependent kinase phosphorylation", 0, None),
                ("Succinate thiokinase (AKA succinyl-CoA synthetase) cleaves a high-energy bond of succinyl-CoA. This high energy bond is of which of the following types?", "Thioester", "Ester", "Carboxylic acid", "Aldehyde", 0, None),
                ("The TCA cycle is also known as which of the following?", "Krebs cycle", "Energy cycle", "Succinate cycle", "GTP cycle", 0, None),
                ("The TCA cycle operates in which of the following compartments?", "Mitochondrion", "Nucleus", "Endoplasmic reticulum", "Golgi apparatus", 0, None),

                # Gluconeogenesis
                ("The primary substrate of gluconeogenesis is which of the following?", "Amino Acids", "Glycerol", "Fatty acids", "Glucose", 0, None),
                ("Which of the following enzymes converts pyruvate to oxaloacetate?", "Pyruvate carboxylase", "Pyruvate dehydrogenase", "Oxaloacetate oxidase", "Complex II", 0, None),
                ("Using gluconeogenesis, how many moles of pyruvate are required to synthesize one mole of glucose?", "2", "1", "3", "4", 0, None),
                ("Which of the following enzymes synthesizes cAMP from ATP?", "Adenylate cyclase", "Phosphodiesterase", "PFK2", "Pyruvate kinase", 0, None),
                ("The Cori cycle involves which of the following?", "Glucose converted to lactate and back to glucose", "Glucose converted to pyruvate and back to glucose", "Glucose converted to glycogen and back to glucose", "Glucose converted to ATP and back to glucose", 0, None),
                ("True/False: Acetyl-CoA + oxaloacetate -> citrate is an anaplerotic reaction.", "False", "True", "None of these", "Both A and B", 0, None),
                ("True/False: Oxaloacetate is permeable to the inner mitochondrial membrane", "False", "True", "None of these", "Both A and B", 0, None),
                ("When insulin levels in the blood are relatively high and glucagon levels are low, which of the following is most likely true?", "FBP-2 is inactive and PFK-2 is active", "Intracellular Fructose 2,6 bisphosphate levels are decreasing", "PFK-2 is inactive and FBP-2 is active", "Gluconeogenesis is active and glycolysis is inactive", 0, None),
                ("Which of the following enzymes covalently modifies the FBP-2/PFK-2 enzyme complex?", "Protein kinase A", "PFK-1", "PFK-2", "Pyruvate kinase", 0, None),
                ("Which of the following results in a futile cycle?", "Both glycolysis and gluconeogenesis are active", "Both glycolysis and gluconeogenesis are inactive", "Glycolysis is active and gluconeogenesis is inactive", "Glycolysis is inactive and gluconeogenesis is active", 0, None),
                ("Glucose-6-phosphatase is located in which of the following cellular compartments?", "Endoplasmic reticulum", "Nucleus", "Nucleolus", "Golgi apparatus", 0, None),
                ("To convert oxaloacetate to malate", "Oxaloacetate must be reduced to malate", "Malate must be reduced to oxaloacetate", "Oxaloacetate must be carboxylated", "Oxaloacetate must be decarboxylated", 0, None),
            ]
            conn.executemany('INSERT INTO questions (question, option1, option2, option3, option4, correct, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)', seed_questions)
            conn.commit()

init_db()


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == APP_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid password. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    # Route Protection
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    with get_db() as conn:
        cursor = conn.execute('SELECT id FROM questions')
        q_ids = [row['id'] for row in cursor.fetchall()]
        random.shuffle(q_ids)
        
    session['question_ids'] = q_ids
    session['current_index'] = 0
    session['score'] = 0
    session['answers_history'] = {}
    
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Route Protection
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if 'question_ids' not in session or not session['question_ids']:
        return render_template('quiz.html', view='empty')
        
    current_index = session['current_index']
    q_ids = session['question_ids']
    total_questions = len(q_ids)
    
    if current_index >= total_questions:
        return redirect(url_for('results'))
        
    q_id = q_ids[current_index]
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'next':
            session['current_index'] += 1
            return redirect(url_for('quiz'))
            
        elif action == 'back':
            if session['current_index'] > 0:
                session['current_index'] -= 1
            return redirect(url_for('quiz'))
            
        elif action == 'submit':
            selected_orig_idx = request.form.get('option')
            if selected_orig_idx is not None:
                with get_db() as conn:
                    cursor = conn.execute('SELECT correct FROM questions WHERE id = ?', (q_id,))
                    row = cursor.fetchone()
                    
                is_correct = (row and int(selected_orig_idx) == row['correct'])
                prev_state = session['answers_history'].get(str(q_id))
                was_previously_correct = prev_state.get('correct') if prev_state else False
                
                if is_correct and not was_previously_correct:
                    session['score'] += 1
                elif not is_correct and was_previously_correct:
                    session['score'] = max(0, session['score'] - 1)
                    
                session['answers_history'][str(q_id)] = {
                    'selected': int(selected_orig_idx),
                    'correct': is_correct
                }
                session.modified = True
                return redirect(url_for('quiz'))

    with get_db() as conn:
        cursor = conn.execute('SELECT * FROM questions WHERE id = ?', (q_id,))
        q_data = cursor.fetchone()
        
    if not q_data:
        session['current_index'] += 1
        return redirect(url_for('quiz'))
        
    options_pool = [
        {'text': q_data['option1'], 'orig_idx': 0},
        {'text': q_data['option2'], 'orig_idx': 1},
        {'text': q_data['option3'], 'orig_idx': 2},
        {'text': q_data['option4'], 'orig_idx': 3}
    ]
    
    random.seed(q_id)
    random.shuffle(options_pool)
    random.seed()
    
    history = session['answers_history'].get(str(q_id))
    
    return render_template(
        'quiz.html', 
        question=q_data['question'], 
        options=options_pool, 
        q_num=current_index + 1, 
        total=total_questions,
        view='question',
        history=history,
        show_back=(current_index > 0),
        image_url=q_data['image_url']
    )

@app.route('/results')
def results():
    # Route Protection
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    score = session.get('score', 0)
    total = len(session.get('question_ids', []))
    return render_template('quiz.html', score=score, total=total, view='results')

if __name__ == '__main__':
    app.run(debug=True)
