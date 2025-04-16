from glob import glob
import json
import uuid
import os
import shutil
files = glob('./*.mha')


CREATE_FOLDERS_AND_FILES=False 

out = []
for f in files:
	main_pk = str(uuid.uuid4())
	file_pk = str(uuid.uuid4())
	obj = {
		"pk": main_pk,
		"inputs": [
			{
				"pk": str(uuid.uuid4()),
				"image": {
					"pk": str(uuid.uuid4()),
					"name": f.split('/')[-1]
				},
				"interface": {
					"pk": str(uuid.uuid4()),
					"slug": "mri-image",
					"relative_path": "images/mri"
				}
			}
		],
		"outputs": [
			{
				"pk": file_pk,
				"image": {
					"pk": str(uuid.uuid4()),
					"name": f"{str(uuid.uuid4())}.mha"
				},
				"interface": {
					"pk": str(uuid.uuid4()),
					"slug": "synthetic-ct-image",
					"relative_path": "images/synthetic-ct"
				}
			}
		]
	}
	out.append(obj)
	if CREATE_FOLDERS_AND_FILES:
		sct_dir = f"{main_pk}/output/images/synthetic-ct"
		os.makedirs(sct_dir)
		shutil.copy(f, f"{sct_dir}/{file_pk}.mha")



with open("predictions.json", 'w') as f:
	f.write(json.dumps(out))
