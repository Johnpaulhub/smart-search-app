from flask import Flask, render_template, request

app = Flask(__name__)

# Sample data representing your scraped results (you can connect your scraper data here later)
scraped_data = {
    1: {
        "title": "Hospitality Industry Overview - Hotels, Tourism, and Guest Services",
        "description": "This guide covers the core pillars of the hospitality industry, focusing on guest satisfaction, hotel operations, and tourism management.",
        "category": "Hospitality & Tourism"
    },
    2: {
        "title": "Customer Care Excellence and Hotel Management",
        "description": "Learn advanced strategies for resolving customer complaints, front-desk management, and delivering unforgettable guest experiences.",
        "category": "Customer Relations"
    }
}

@app.route('/')
def home():
    # Pass the dictionary items to the home page template
    return render_template('index.html', results=scraped_data)

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    # Get the specific item based on the ID clicked, or show a 404 if not found
    item = scraped_data.get(item_id)
    if not item:
        return "Item not found!", 404
    return render_template('detail.html', item=item)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
