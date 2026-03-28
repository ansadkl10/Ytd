import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pytubefix import YouTube

app = Flask(__name__)
# മറ്റ് വെബ്സൈറ്റുകളിൽ നിന്നോ ബോട്ടുകളിൽ നിന്നോ ഈ API വിളിക്കാൻ CORS സഹായിക്കും
CORS(app)

@app.route('/fetch', methods=['GET'])
def get_link():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"ok": False, "message": "YouTube URL നൽകുക!"}), 400

    try:
        # 'use_oauth=False' നൽകുന്നത് ലോഗിൻ ഒഴിവാക്കാൻ സഹായിക്കും
        yt = YouTube(video_url, use_oauth=False)
        
        # 720p അല്ലെങ്കിൽ 360p വരെയുള്ള 'Progressive' സ്ട്രീം എടുക്കുന്നു 
        # (ഇതാണ് കുക്കികൾ ഇല്ലാതെ കിട്ടാൻ എളുപ്പമുള്ള വഴി)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if stream:
            return jsonify({
                "ok": True,
                "title": yt.title,
                "thumbnail": yt.thumbnail_url,
                "duration": yt.length,
                "quality": stream.resolution,
                "download_link": stream.url  # ഇതാണ് നിങ്ങൾ ചോദിച്ച ഡയറക്ട് ലിങ്ക്
            })
        else:
            return jsonify({"ok": False, "message": "ഡയറക്ട് ലിങ്ക് കണ്ടെത്താനായില്ല!"}), 404

    except Exception as e:
        return jsonify({
            "ok": False, 
            "message": "Error സംഭവിച്ചു!",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    # Koyeb പോർട്ട് 8080 ആണ് സാധാരണ ഉപയോഗിക്കുന്നത്
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

