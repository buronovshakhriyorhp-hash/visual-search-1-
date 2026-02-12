import os
import json
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import faiss
import glob
from torch.utils.data import Dataset, DataLoader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("indexer")

class ImageDataset(Dataset):
    def __init__(self, image_paths, transform=None):
        self.image_paths = image_paths
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        try:
            image = Image.open(img_path).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, img_path
        except Exception:
            return None, img_path

def collate_fn(batch):
    batch = [b for b in batch if b[0] is not None]
    if not batch:
        return None, None
    images, paths = zip(*batch)
    return torch.stack(images), paths

def build_index_batched(image_dir, index_path="data/deepfashion.index", metadata_path="data/metadata.json", batch_size=32):
    logger.info(f"Building index from {image_dir} with batch size {batch_size}")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet50(pretrained=True)
    model.eval()
    model.to(device)
    model = torch.nn.Sequential(*list(model.children())[:-1])

    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    image_paths = glob.glob(os.path.join(image_dir, "*.*"))
    valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    image_paths = [p for p in image_paths if os.path.splitext(p)[1].lower() in valid_extensions]
    
    if not image_paths:
        logger.warning("No images found.")
        return

    dataset = ImageDataset(image_paths, transform=preprocess)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0, collate_fn=collate_fn)

    features_list = []
    metadata = []
    
    with torch.no_grad():
        for i, (images, paths) in enumerate(dataloader):
            if images is None: continue
            
            images = images.to(device)
            embeddings = model(images)
            embeddings = embeddings.cpu().numpy().flatten().reshape(images.size(0), -1).astype('float32')
            
            features_list.append(embeddings)
            
            for path in paths:
                filename = os.path.basename(path)
                
                # Copy image to uploads directory for frontend serving
                target_dir = os.path.join("uploads", "local_dataset")
                os.makedirs(target_dir, exist_ok=True)
                target_path = os.path.join(target_dir, filename)
                import shutil
                try:
                    shutil.copy2(path, target_path)
                except Exception as e:
                    logger.warning(f"Failed to copy {path}: {e}")

                metadata.append({
                    "id": len(metadata),
                    "name": os.path.splitext(filename)[0].replace("_", " ").title(),
                    "price": f"${np.random.randint(20, 200)}",
                    "image": f"http://localhost:8001/uploads/local_dataset/{filename}",
                    "path": target_path
                })
            
            logger.info(f"Processed batch {i+1}/{len(dataloader)}")

    if features_list:
        features_matrix = np.vstack(features_list)
        dimension = features_matrix.shape[1]
        
        index = faiss.IndexFlatL2(dimension)
        index.add(features_matrix)
        
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        faiss.write_index(index, index_path)
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)
            
        logger.info(f"Index built! Saved to {index_path}")
    else:
        logger.error("Indexing failed.")

if __name__ == "__main__":
    import sys
    dataset_dir = sys.argv[1] if len(sys.argv) > 1 else "dataset"
    if not os.path.exists(dataset_dir):
        logger.warning(f"Directory {dataset_dir} does not exist.")
        os.makedirs(dataset_dir, exist_ok=True)
    else:
        build_index_batched(dataset_dir)
