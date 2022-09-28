.PHONY: 3d-viewer 3d-viewer-gpu cc-rabbit-0d cc-rabbit-1d cc-rabbit-2d csv-table dy-static-file-server dy-static-file-server-dynamic-sidecar dy-static-file-server-dynamic-sidecar-compose-spec jupyter-base-notebook jupyter-neuron jupyter-r-notebook jupyter-scipy-notebook kember mapcore-widget mattward-dash raw-graphs raw-graphs-table server tissue-properties 

3d-viewer:
	docker-compose build 3d-viewer
	docker push registry:5000/simcore/services/dynamic/3d-viewer:3.0.4
 
3d-viewer-gpu:
	docker-compose build 3d-viewer-gpu
	docker push registry:5000/simcore/services/dynamic/3d-viewer-gpu:3.0.4
 
cc-0d-viewer:
	docker-compose build cc-0d-viewer
	docker push registry:5000/simcore/services/dynamic/cc-0d-viewer:3.0.5
 
cc-1d-viewer:
	docker-compose build cc-1d-viewer
	docker push registry:5000/simcore/services/dynamic/cc-1d-viewer:3.0.5
 
cc-2d-viewer:
	docker-compose build cc-2d-viewer
	docker push registry:5000/simcore/services/dynamic/cc-2d-viewer:3.0.6
 
csv-table:
	docker-compose build csv-table
	docker push registry:5000/simcore/services/dynamic/csv-table:1.0.1
 
jupyter-base-notebook:
	docker-compose build jupyter-base-notebook
	docker push registry:5000/simcore/services/dynamic/jupyter-base-notebook:2.14.1
 
jupyter-r-notebook:
	docker-compose build jupyter-r-notebook
	docker push registry:5000/simcore/services/dynamic/jupyter-r-notebook:2.14.1
 
jupyter-scipy-notebook:
	docker-compose build jupyter-scipy-notebook
	docker push registry:5000/simcore/services/dynamic/jupyter-scipy-notebook:2.14.1
 
kember-viewer:
	docker-compose build kember-viewer
	docker push registry:5000/simcore/services/dynamic/kember-viewer:2.14.1
 
mapcore-widget:
	docker-compose build mapcore-widget
	docker push registry:5000/simcore/services/dynamic/mapcore-widget:0.1.25
 
mattward-viewer:
	docker-compose build mattward-viewer
	docker push registry:5000/simcore/services/dynamic/mattward-viewer:3.0.6
 
raw-graphs:
	docker-compose build raw-graphs
	docker push registry:5000/simcore/services/dynamic/raw-graphs:2.11.2
 
raw-graphs-table:
	docker-compose build raw-graphs-table
	docker push registry:5000/simcore/services/dynamic/raw-graphs-table:2.11.2
  
tissue-properties:
	docker-compose build tissue-properties
	docker push registry:5000/simcore/services/dynamic/tissue-properties:1.0.2
 

publish_all:
	docker tag registry:5000/simcore/services/dynamic/3d-viewer:3.0.4 itisfoundation/3d-viewer:3.0.4
	docker push itisfoundation/3d-viewer:3.0.4
 
	docker tag registry:5000/simcore/services/dynamic/3d-viewer-gpu:3.0.4 itisfoundation/3d-viewer-gpu:3.0.4
	docker push itisfoundation/3d-viewer-gpu:3.0.4
 
	docker tag registry:5000/simcore/services/dynamic/cc-0d-viewer:3.0.5 itisfoundation/cc-0d-viewer:3.0.5
	docker push itisfoundation/cc-0d-viewer:3.0.5
 
	docker tag registry:5000/simcore/services/dynamic/cc-1d-viewer:3.0.5 itisfoundation/cc-1d-viewer:3.0.5
	docker push itisfoundation/cc-1d-viewer:3.0.5
 
	docker tag registry:5000/simcore/services/dynamic/cc-2d-viewer:3.0.6 itisfoundation/cc-2d-viewer:3.0.6
	docker push itisfoundation/cc-2d-viewer:3.0.6
 
	docker tag registry:5000/simcore/services/dynamic/csv-table:1.0.1 itisfoundation/csv-table:1.0.1
	docker push itisfoundation/csv-table:1.0.1
 
	docker tag registry:5000/simcore/services/dynamic/jupyter-base-notebook:2.14.1 itisfoundation/jupyter-base-notebook:2.14.1
	docker push itisfoundation/jupyter-base-notebook:2.14.1
 
	docker tag registry:5000/simcore/services/dynamic/jupyter-r-notebook:2.14.1 itisfoundation/jupyter-r-notebook:2.14.1
	docker push itisfoundation/jupyter-r-notebook:2.14.1
 
	docker tag registry:5000/simcore/services/dynamic/jupyter-scipy-notebook:2.14.1 itisfoundation/jupyter-scipy-notebook:2.14.1
	docker push itisfoundation/jupyter-scipy-notebook:2.14.1
 
	docker tag registry:5000/simcore/services/dynamic/kember-viewer:2.14.1 itisfoundation/kember-viewer:2.14.1
	docker push itisfoundation/kember-viewer:2.14.1
 
	docker tag registry:5000/simcore/services/dynamic/mapcore-widget:0.1.25 itisfoundation/mapcore-widget:0.1.25
	docker push itisfoundation/mapcore-widget:0.1.25
 
	docker tag registry:5000/simcore/services/dynamic/mattward-viewer:3.0.6 itisfoundation/mattward-viewer:3.0.6
	docker push itisfoundation/mattward-viewer:3.0.6
 
	docker tag registry:5000/simcore/services/dynamic/raw-graphs:2.11.2 itisfoundation/raw-graphs:2.11.2
	docker push itisfoundation/raw-graphs:2.11.2
 
	docker tag registry:5000/simcore/services/dynamic/raw-graphs-table:2.11.2 itisfoundation/raw-graphs-table:2.11.2
	docker push itisfoundation/raw-graphs-table:2.11.2
 
	docker tag registry:5000/simcore/services/dynamic/tissue-properties:1.0.2 itisfoundation/tissue-properties:1.0.2
	docker push itisfoundation/tissue-properties:1.0.2
 