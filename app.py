from flask import Flask, jsonify
from flask import request
import lucene
import sys
from ConfigParser import *
from lucene import \
    SimpleFSDirectory, System, File, \
    Document, Field, StandardAnalyzer, IndexWriter, Version

# imports related to lucene

indexDir = "/tmp/luceneindex"

app = Flask(__name__)
# lucene_dir = "/tmp/luceneindex"

@app.route('/' , methods=['POST','GET'])
def index():
    if request.method == 'POST':
        return request.form['product'].upper()
    else:
	return 'Flask is good with Get Method..:P'

@app.route('/_get_data' , methods=['POST','GET'])
def names():
    lst = []
    
    search = "spax"#request.form['product']
    lucene.initVM()
    
    dir = SimpleFSDirectory(File(indexDir))
    analyzer = StandardAnalyzer(Version.LUCENE_30)
    searcher = IndexSearcher(dir)

    query = QueryParser(lucene.Version.LUCENE_CURRENT, "text", analyzer).parse(search)
    MAX = 1000
    hits = searcher.search(query, MAX)

    print "Found %d document(s) that matched query '%s':" % (hits.totalHits, query)

    for hit in hits.scoreDocs:
        if hit.score >= 1:
            print hit.score, hit.doc, hit.toString()
            doc = searcher.doc(hit.doc)
            print doc.get("text").encode("utf-8")
            items = doc.get("text").encode("utf-8").split(',')
            for item in items:
                if item == search:
                    pass
                elif item not in lst:
                    lst.append(item)
    #print lst
    data = {"products": lst}
    if request.method == 'POST':
        return jsonify(data)
    else:
	return jsonify(data)
    
    
@app.route('/demo' , methods=['POST','GET'])
def index1():
    if request.method == 'POST':
        query_var = request.form['product'].upper()
        # search for it using lucene retriever
        #op = lucene_retriever(query_var) # Handle exception
        #return op
	return query_var
    else:
	return request.form['product'].upper()

#def lucene_retriver(text):
    # search for that text in index
    # return line

# Before all requests, build lucene index

@app.before_first_request
def configure_lucene():
    
    f = open('clique.txt','r')
    lucene.initVM()
    print 'Inside Function'
    #indexDir = "/tmp/luceneindex"
    dir = SimpleFSDirectory(File(indexDir))
    analyzer = StandardAnalyzer(lucene.Version.LUCENE_CURRENT)
    writer = IndexWriter(dir, analyzer, True, IndexWriter.MaxFieldLength(512))

    print >> sys.stderr, "Currently there are %d documents in the index..." % writer.numDocs()

    print >> sys.stderr, "Reading lines from sys.stdin..."
    for line in f:
        line = line.replace('\t','')
        line = line.replace('\r','')
        line = line.replace('\n','')
  	line = line.replace('^','')
    	line = line.strip()
        doc = Document()
        doc.add(Field("text", line, Field.Store.YES, Field.Index.ANALYZED))
        writer.addDocument(doc)

    print >> sys.stderr, "Indexed lines from stdin (%d documents in index)" % (writer.numDocs())
    print >> sys.stderr, "About to optimize index of %d documents..." % writer.numDocs()
    writer.optimize()
    print >> sys.stderr, "...done optimizing index of %d documents" % writer.numDocs()
    print >> sys.stderr, "Closing index of %d documents..." % writer.numDocs()
    writer.close()
    #print >> sys.stderr, "...done closing index of %d documents" % writer.numDocs()

    # Map reduce output path (cliques) -> local file
    # indexer initialize (as given in indexer)
    #with open(map_reduce_op, 'r') as inf:
    #    for line in inf:
            # add line to lucene index
            # Lucene index directory should be a global


if __name__ == '__main__':
    app.run()
