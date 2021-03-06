# -*- coding: utf-8 -*-


import kindred
from intervaltree import IntervalTree
from collections import defaultdict

class Parser:
	"""
	Runs Spacy on corpus to get sentences and associated tokens
	"""
	
	def __init__(self,language='en'):
		"""
		Create a Parser object that will use Spacy for parsing. It uses Spacy and offers all the same languages that Spacy offers. Check out: https://spacy.io/usage/models. Note that the language model needs to be downloaded first (e.g. python -m spacy download en)
		
		:param language: Language to parse (en/de/es/pt/fr/it/nl)
		:type language: str
		"""

		# We only load spacy if a Parser is created (to allow ReadTheDocs to build the documentation easily)
		import spacy

		acceptedLanguages = ['en','de','es','pt','fr','it','nl']
		assert language in acceptedLanguages, "Language for parser (%s) not in accepted languages: %s" % (language,str(acceptedLanguages))

		self.language = language

		self.nlp = spacy.load(language, disable=['ner'])

	def _sentencesGenerator(self,text):
		parsed = self.nlp(text)
		sentence = None
		for token in parsed:
			if sentence is None or token.is_sent_start:
				if not sentence is None:
					yield sentence
				sentence = []
			sentence.append(token)

		if not sentence is None and len(sentence) > 0:
			yield sentence

	def parse(self,corpus):
		"""
		Parse the corpus. Each document will be split into sentences which are then tokenized and parsed for their dependency graph. All parsed information is stored within the corpus object.
		
		:param corpus: Corpus to parse
		:type corpus: kindred.Corpus
		"""

		assert isinstance(corpus,kindred.Corpus)

		for d in corpus.documents:
		#for doctokens in self.nlp.pipe( d.text for d in corpus.documents, batch_size=2, n_threads=1):
			entityIDsToEntities = d.getEntityIDsToEntities()
		
			denotationTree = IntervalTree()
			entityTypeLookup = {}
			for e in d.getEntities():
				entityTypeLookup[e.entityID] = e.entityType
			
				for a,b in e.position:
					if b > a:
						denotationTree[a:b] = e.entityID
				
			for sentence in self._sentencesGenerator(d.text):
				tokens = []
				for t in sentence:
					token = kindred.Token(t.text,t.lemma_,t.pos_,t.idx,t.idx+len(t.text))
					tokens.append(token)

				sentenceStart = tokens[0].startPos
				sentenceEnd = tokens[-1].endPos
				sentenceTxt = d.text[sentenceStart:sentenceEnd]

				indexOffset = sentence[0].i
				dependencies = []
				for t in sentence:
					depName = t.dep_
					dep = (t.head.i-indexOffset,t.i-indexOffset,depName)
					dependencies.append(dep)

				# TODO: Should I filter this more or just leave it for simplicity
					
				entityIDsToTokenLocs = defaultdict(list)
				for i,t in enumerate(tokens):
					entitiesOverlappingWithToken = denotationTree[t.startPos:t.endPos]
					for interval in entitiesOverlappingWithToken:
						entityID = interval.data
						entityIDsToTokenLocs[entityID].append(i)

				# Let's gather up the information about the "known" entities in the sentence
				entitiesWithLocations = []
				for entityID,entityLocs in sorted(entityIDsToTokenLocs.items()):
					e = entityIDsToEntities[entityID]
					entityWithLocation = (e, entityLocs)
					entitiesWithLocations.append(entityWithLocation)
					
				sentence = kindred.Sentence(sentenceTxt, tokens, dependencies, entitiesWithLocations, d.getSourceFilename())
				d.addSentence(sentence)

		corpus.parsed = True

