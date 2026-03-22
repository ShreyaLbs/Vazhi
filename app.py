from flask import Flask, render_template, request, jsonify
import json
import re

app = Flask(__name__)

def find_schemes(user_message):
    with open("schemes.json", "r", encoding="utf-8") as f:
        schemes_data = json.load(f)["schemes"]
        
    message = user_message.lower()
    matched_schemes = []
    
    for scheme in schemes_data:
        # Check eligibility tags and description
        keywords = scheme["eligibility"] + scheme["name"].lower().split() + scheme["description"].lower().split()
        
        # Simple keyword matching
        match_score = 0
        for word in message.split():
            if len(word) > 2 and any(word in kw.lower() for kw in keywords):
                match_score += 1
                
        if match_score > 0:
            matched_schemes.append((match_score, scheme))
            
    # Sort by relevance
    matched_schemes.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in matched_schemes] # Return all matches

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    lang = request.json.get("lang", "eng")
    
    if not user_message:
        return jsonify({"response": "Please tell me a bit about yourself or what kind of help you are looking for."})
        
    greetings = ["hi", "hello", "hey", "namaskaram"]
    if any(greet == user_message.lower().strip() for greet in greetings):
        return jsonify({
            "response": "Namaskaram! 🙏 I am Vazhi, your guide to government schemes in Kerala. Tell me a bit about yourself (e.g., 'I am a student from low-income family' or 'health schemes for BPL')." if lang == "eng" else "നമസ്കാരം! 🙏 ഞാൻ 'വഴി'. സർക്കാർ പദ്ധതികൾ കണ്ടെത്താൻ ഞാൻ നിങ്ങളെ സഹായിക്കാം."
        })
        
    matched = find_schemes(user_message)
    
    if matched:
        response_text = "Here are some top-matching schemes you are likely eligible for:<br><br>" if lang == "eng" else "നിങ്ങൾക്ക് അനുയോജ്യമായ ചില പദ്ധതികൾ താഴെ നൽകുന്നു:<br><br>"
        cards_html = ""
        for s in matched:
            docs_html = "".join([f"<label><input type='checkbox'> {doc}</label><br>" for doc in s.get('documents', [])])
            cards_html += f"""
            <div class='scheme-card glass-card'>
                <div class='card-header'>
                    <span class='match-badge'>⭐ Top Match</span>
                </div>
                <h4>{s['name']}</h4>
                <p>{s['description']}</p>
                
                <div class='doc-checklist'>
                    <strong>📋 Important Required Docs:</strong><br>
                    {docs_html}
                </div>

                <div class='tags'>
                    {''.join([f"<span class='tag'>{tag}</span>" for tag in s['eligibility']])}
                </div>
                <div class='card-actions'>
                    <a href='{s['link']}' target='_blank' class='apply-btn'>Apply Now ↗</a>
                    <a href='whatsapp://send?text=Check out the {s['name']} scheme on Vazhi! It provides: {s['description']}. Apply here: {s['link']}' class='wa-btn'>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                    </a>
                </div>
            </div>
            """
        return jsonify({"response": response_text + cards_html})
    else:
        return jsonify({
            "response": "I couldn't find a specific scheme for that right now. Could you tap one of the quick topics?" if lang == "eng" else "ക്ഷമിക്കണം, ഈ വിവരങ്ങൾക്കനുസരിച്ച് പദ്ധതികൾ കണ്ടെത്താനായില്ല. ദയവായി മറ്റ് ബട്ടണുകൾ ഉപയോഗിക്കുക."
        })

if __name__ == "__main__":
    app.run(debug=True)