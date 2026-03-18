Copy-Item -Force data\examples\docs.jsonl data\raw\docs.jsonl
Copy-Item -Force data\examples\graph_edges.json data\raw\graph_edges.json
Write-Output "sample data copied to data/raw"
