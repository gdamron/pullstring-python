init:

install:
	python setup.py install

test:
	(cd tests ; ./test_webapi.py)

example:
	(cd examples ; ./chatclient.py 9fd2a189-3d57-4c02-8a55-5f0159bff2cf e50b56df-95b7-4fa1-9061-83a7a9bea372)

clean:
	find . -name *.pyc -print0 | xargs -0 rm -f
	find . -name *~ -print0 | xargs -0 rm -f
	find . -name '#*#' -print0 | xargs -0 rm -f
