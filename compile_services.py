import os
import json
import re

INPUT_DIR = "data/catalog"
OUTPUT_FILE = "backend/services.json"

def slugify(text: str) -> str:
    # Convert to lowercase
    t = text.lower()
    # Replace any non-alphanumeric character with an underscore
    t = re.sub(r'[^a-z0-9]', '_', t)
    # Replace multiple underscores with a single one
    t = re.sub(r'_+', '_', t)
    # Strip leading/trailing underscores
    return t.strip('_')

def compile_catalog():
    if not os.path.exists(INPUT_DIR):
        print(f"Error: {INPUT_DIR} does not exist!")
        return

    services = []
    
    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".json"):
            continue
            
        file_path = os.path.join(INPUT_DIR, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            service_name = data.get("service") or data.get("title") or filename.replace(".json", "").replace("_", " ")
            if service_name.strip() == "R T I":
                service_name = "RTI"
            service_id = slugify(service_name)
            
            # Extract keywords from use_cases
            keywords = data.get("use_cases", [])
            if not keywords:
                # Fallback to splitting name
                keywords = [w.strip().lower() for w in re.split(r'\s+|_', service_name) if len(w) > 1]
                
            service_entry = {
                "id": service_id,
                "name": service_name,
                "url": data.get("url", ""),
                "requires_login": data.get("requires_login", False),
                "description": data.get("description", f"Delhi Police service for {service_name}"),
                "keywords": keywords
            }
            
            services.append(service_entry)
            print(f"Processed: {service_name} -> {service_id}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    # Write to backend/services.json
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump({"services": services}, out, indent=2, ensure_ascii=False)
        
    print(f"\nSuccessfully compiled {len(services)} services into {OUTPUT_FILE}!")

if __name__ == "__main__":
    compile_catalog()
