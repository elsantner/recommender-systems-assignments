# Recommender Systems project ideas
*Antonios Marinidis, Elias Santner & Jana Siebert*
## (Potentially) relevant information in movies_tmdbMeta
- title
- overview (i.e. plot description)
- director
- cast
- budget
- popularity
- release date
- runtime
- original language
- spoken languages
- production countries

## Strategy ideas
**Task:** Develop a number of (at least 5) functions in Python that, given a _reference_ _movie_ _ID_ (_mref_), return a ranked list of the top-5 most similar items. Each function has to implement a different strategy.

### 1. Genre overlap & movie popularity (_Antonios Marinidis_)
Rank by simple genre overlap with _mref_ and movie popularity.

### 2. Title & Overview TF-IDF (_Jana Siebert_)
Rank movies by the similarity of _title_ and _overview_ with _mref_.
Use Longest Common Subsentence (LCS) for _title_ and TF-IDF for _overview_.

*Note: Might not be good in practice, but aims at recommending **similar** items.*

### 3. Directors, actors & popularity (_Antonios Marinidis_)
Select movies which have a "significant" director and actor overlap with _mref_.
Sort these movies by popularity.
If not enough director overlap exists, use just actor overlap.
*Maybe include genre overlap as well!*

### 4. Runtime, original language and production countries (_Elias Santner_)
Select movies which have a "similar" runtime (+/- _n_ minutes), the same original language and production countries.
Rank by popularity.

### 5. Actors, genres and release year (_Elias Santner_)
Select movies within a similar release time frame to _mref_, e.g. +/- 2 years.
Sort these movies by actor and genre similarity (using Cosine or Jaccard-based similarity measures).

*Apply step-by-step: release year, genre sim and rank by actor sim.*

## Questions
- Do we always have to recommend *exactly 5* items? - **10 items!**
