# MSApriori
It generalizes the Apriori algorithm for finding frequent itemsets. When there is only one MIS value (for all items), it reduces to the Apriori algorithm.
Minimum support apriori generates different itemsets to satisfy different minimum supports, depending on what items are in the itemsets. 
This model thus enables us to achieve our objective of finding itemsets involving rare items without causing frequent items to generate too many meaningless itemsets.


usage: test.py [INPUT] [PARAMETER] [OUTPUT]

For example you could use the following: python3 lashd.py input.txt parameter-file.txt output.txt

The output is of the form:
  3 : {30, 80}
Tailcount = 6
 
3 is the frequency count of the pattern {70, 10} in the data. Tailcount is the frequency count of the tail of the pattern, {10}.
