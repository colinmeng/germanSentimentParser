# Credits

The dataset was created by Oliver Guhr and ist publically available on his [GitHubPage](https://github.com/oliverguhr/german-sentiment).
The corresponding paper can be found [here](http://www.lrec-conf.org/proceedings/lrec2020/pdf/2020.lrec-1.202.pdf).

## My sub-dataset

For my work I needed balanced Datasets, where the number of reviews per rating (1-6) is equal. I created subsets with 200, 2000, 10000 and 20000 entries per rating each and filtered out all reviews with no correct rating. The reviews were selected by order (top-to-bottom), so the 200-entries-subset is fully included in the 2000-entries-subset.