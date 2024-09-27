from glob import glob
import json
import uuid
files = glob('./*.mha')

out = []
for f in files:
	obj = {
		"pk": str(uuid.uuid4()),
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
				"pk": str(uuid.uuid4()),
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

with open("predictions.json", 'w') as f:
	f.write(json.dumps(out))
