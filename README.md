# Refactoring non-idiomatic Python code into idiomatic Python code

1. ## Web application: 
	We develop a web application for the code refactoring, you could access the application through the url: 47.242.131.128:5000
	
	Each time, you could click code area to refresh.
	
2. ## Evaluation result:
	1). ./evaluation_data/code_review_total_code_900: 

            Code review evaluation result

	2). ./evaluation_data/testing: 
           
            Testing evaluation result
	
	3). ./evaluation_data/pull request 90.csv: 
  
           Pull requests result

3. ## Code:
	1).  ./code/crawl_repos_python: 
	
	    crawling top 10000 Python repositories by the number of stars from GitHub and extracting Python 3 repositories
	
	2). ./code/extract_idiom_code:
	  
	    extracting idiomatic code
	
	3).  ./code/extract_complicate_code: 
	
	    extracting non-idiomatic code
	
	4).  ./code/transform_c_s: 
	
	    refactoring non-idiomatic code into idiomatic code
	
	5).  ./code/test_case:
	 
	     configuring projects and executing test cases
	
	6).  ./code/motivation: 
	
	    comparing the performance of non-idiomatic code and the corresponding idiomatic code
	
	7). ./data: 
	    Storing the result of running the code. Particularly, we save all code pairs of 
	    non-idiomatic and corresponding idiomatic Python code for nine pythonic idioms in transform_complicate_to_simple_pkl.zip, which could be download in <a href="https://zenodo.org/record/6367738#.YjRzLxBBzdo">link</a>.


