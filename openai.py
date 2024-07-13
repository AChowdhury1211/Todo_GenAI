from langchain.llms import OpenAI
from flask import request
from models import db

openai = OpenAI(api_key='your_openai_api_key')

@routes.route('/query-todos', methods=['POST'])
@jwt_required()
def query_todos():
    user_id = get_jwt_identity()
    query = request.get_json().get('query')

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=f"Convert the following natural language query to SQL: {query}",
        max_tokens=100
    )

    sql_query = response.choices[0].text.strip()
    result = db.session.execute(sql_query).fetchall()
    return jsonify([dict(row) for row in result])
