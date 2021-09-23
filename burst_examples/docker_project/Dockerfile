FROM burstableai/burst_base:ubu2004
COPY --from=docker:19.03 /usr/local/bin/docker /usr/local/bin/
# CMD ["python3", "-c", "import os;print (os.path.exists('./project/doctest.py'))"]
# CMD ["python3", "-c", "import os;print (os.path.abspath('.'))"]
WORKDIR /home/burst/work/project
CMD ["python3", "doctest.py"]
