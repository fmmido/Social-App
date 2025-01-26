# content/content_creation.py

from blockchain.blockchain import Blockchain
import uuid  # For generating unique post IDs

blockchain = Blockchain() # Create it as a global variable for now

def create_post(user_id, content, media=None):
  post_id = str(uuid.uuid4()) # Generate unique ID
  timestamp = datetime.datetime.now()

  post_data = {
      "id": post_id,
      "user_id": user_id,
      "content": content,
      "timestamp": timestamp,
      "media": media # Add media handling logic
  }

  # Add post to blockchain
  blockchain.add_block(post_data)
  return post_id


# blockchain/blockchain.py - modified add_block
# ... inside Blockchain class:
def add_block(self, data):
  # ...  (existing code)
  # Add validation or verification here before adding to chain!
  self.chain.append(new_block)