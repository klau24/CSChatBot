import sql_queries
from query_classifier import QueryClassifier
from entity_classifier import EntityClassifier
import spacy

nlp = spacy.load("en_core_web_sm")


class ChatBot:
    def __init__(self):
        self.entityClf = EntityClassifier()
        self.queryClf = QueryClassifier()

    # Given a query, returns tokenized query with adjacent nouns grouped together
    def group_tokens(self, q):
        doc = nlp(q)
        tokenized = []
        for token in doc:
            if token.tag_[:2] in ["NN", "CD", "HY"] and tokenized[-1][1] == "NN":
                tokenized[-1][0] += " " + token.text
            elif token.tag_[:2] == "NN":
                tokenized.append([token.text, "NN"])
            else:
                tokenized.append([token.text, token.tag_])
        return tokenized

    # Given tokenized query, substitutes recognized entities with entity tags
    # Returns extracted entities and new query with tags
    def subst_entities(self, tokens):
        new_q = ""
        entities = {}
        for token in tokens:
            if token[1] == "NN":
                ent = self.entityClf.predict(token[0])[0]
                if ent != "NON-ENTITY":
                    entities[ent] = token[0]
                    new_q += " [{}]".format(ent)
                else:
                    new_q += " {}".format(token[0])
            else:
                new_q += " {}".format(token[0])
        return entities, new_q

    # Given a query, prints responses from similar questions
    def get_sample_answers(self, q):
        tokens = self.group_tokens(q)
        entities, new_q = self.subst_entities(tokens)
        print(tokens)
        print(entities)
        print(new_q)
        answer = self.queryClf.get_answer(new_q)
        return entities, answer


if __name__ == "__main__":
    bot = ChatBot()
    print("Hello I am EKK, your Cal Poly Virtual Assistant. How can I help you today?")
    q = input("Q> ")
    while q != "exit" and q != "Exit":
        entities, answer = bot.get_sample_answers(q)
        query = sql_queries.Query(entities, answer)
        query.queryDB()
        q = input("Q> ")
