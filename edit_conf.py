my_file = open("/etc/neo4j/neo4j.conf")
string_list = my_file.readlines()
my_file.close()

old_lines = [
"#dbms.default_database=neo4j\n",
"#dbms.memory.heap.initial_size=512m\n",
"#dbms.memory.heap.max_size=512m\n",
"#dbms.memory.pagecache.size=10g\n",
"#dbms.security.procedures.unrestricted=my.extensions.example,my.procedures.*\n",
"#dbms.security.procedures.allowlist=apoc.coll.*,apoc.load.*,gds.*\n"
]

new_lines = [
"dbms.default_database=keywords\n",
"dbms.memory.heap.initial_size=3G\n",
"dbms.memory.heap.max_size=6G\n",
"dbms.memory.pagecache.size=6G\n",
"dbms.security.procedures.unrestricted=apoc.*\n",
"dbms.security.procedures.allowlist=apoc.coll.*,apoc.load.*,apoc.*\n"
]

for old_line, new_line in zip(old_lines,new_lines):
	if old_line in string_list:
		idx = string_list.index(old_line)
		string_list[idx] = new_line

my_file = open("/etc/neo4j/neo4j.conf", "w")
new_file_contents = "".join(string_list)
my_file.write(new_file_contents)
my_file.close()