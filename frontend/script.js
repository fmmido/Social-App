       // Global variables
       let currentUserId = null;
       let currentUsername = null;
       let currentUserProfile = null;

       function toggleSections(loggedIn) {
           // Main content sections
            document.getElementById('create-post').style.display = loggedIn ? 'block' : 'none';
           document.getElementById('timeline').style.display = loggedIn ? 'block' : 'none';
           document.getElementById('direct-messages').style.display = loggedIn ? 'block' : 'none';
           document.getElementById('trending-topics').style.display = loggedIn ? 'block' : 'none';
           document.getElementById('search-section').style.display = loggedIn ? 'block' : 'none';
            document.getElementById('bookmarks-section').style.display = loggedIn ? 'block' : 'none';
           document.getElementById('mute-section').style.display = loggedIn ? 'block' : 'none';
             document.getElementById('spaces-section').style.display = loggedIn ? 'block' : 'none';
           document.getElementById('moments-section').style.display = loggedIn ? 'block' : 'none';
           document.getElementById('analytics-section').style.display = loggedIn ? 'block' : 'none';
           document.getElementById('polls-section').style.display = loggedIn ? 'block' : 'none';
           document.getElementById('notifications-section').style.display = loggedIn ? 'block' : 'none';
           document.getElementById('edit-profile-section').style.display = loggedIn ? 'block' : 'none';


           // Navigation bar user info
           document.getElementById('nav-user-info').style.display = loggedIn ? 'flex' : 'none';
           document.getElementById('logout-button').style.display = loggedIn ? 'block' : 'none';
             // Enable/disable menu buttons
           document.querySelectorAll('.menu-button').forEach(button => {
               button.disabled = !loggedIn;
               button.classList.toggle('disabled',!loggedIn);
           });
       }
        // Function to hide all sections
       function hideAllSections() {
          const sections = document.querySelectorAll('main > section, .right-sidebar > section, .main-content > section');
           sections.forEach(section => {
             section.style.display = 'none';
           })
       }

       // Function to handle user registration
       async function registerUser() {
           const username = document.getElementById('username').value;
           const password = document.getElementById('password').value;

           const response = await fetch('/api/register', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ username, password })
           });

           const data = await response.json();
           if (response.status === 201) {
               document.getElementById('user-message').textContent = 'Registration successful! Please login.';
           } else {
               document.getElementById('user-message').textContent = data.error || 'Registration failed.';
           }
       }

       // Function to handle user login
       async function loginUser() {
           const username = document.getElementById('username').value;
           const password = document.getElementById('password').value;

           const response = await fetch('/api/login', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ username, password })
           });

           if (response.status === 200) {
               const data = await response.json();
               currentUserId = data.userId;
                document.getElementById('user-message').textContent = 'Login successful!';
               await fetchCurrentUser();
               toggleSections(true);
               loadPosts();
                loadTrendingTopics();
               loadDMs();
                document.getElementById('user-section').style.display =  'none';
           }
            else {
               const data = await response.json();
                document.getElementById('user-message').textContent = data.error || 'Login failed.';
            }
       }
       // Function to handle user logout
       async function logoutUser(){
            const response = await fetch('/api/logout', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' }
           });

           if (response.status === 200){
                 currentUserId = null;
                 currentUsername = null;
                   currentUserProfile = null;
                document.getElementById('nav-username').textContent = '';
                toggleSections(false);
                hideAllSections()
                document.getElementById('user-message').textContent = 'Logged out successfully';
               document.getElementById('user-section').style.display =  'block';


           }else {
                 const data = await response.json();
                 document.getElementById('user-message').textContent = data.error || 'Logout failed'
           }

       }
        // Function to fetch and display current user info
       async function fetchCurrentUser() {
          const response = await fetch('/api/current_user', {
               method: 'GET',
               headers: { 'Content-Type': 'application/json' },
           });
           if (response.status === 200) {
               const data = await response.json();
                currentUserId = data.userId;
                currentUsername = data.username;
                   currentUserProfile = data.profile;
               document.getElementById('nav-username').textContent =  `Logged in as: ${currentUsername}`;
                toggleSections(true);

           }
            else if (response.status === 401){
                toggleSections(false);
                hideAllSections()
                console.log('User is not logged in');
            }else{
               console.error("error fetching current user", response)
            }
       }
         async function editProfile(){
           const bio = document.getElementById('edit-bio').value;
           const location = document.getElementById('edit-location').value;
           const website = document.getElementById('edit-website').value;
            if(!bio && !location && !website){
               alert("Please provide at least one field to update");
               return;
           }
            const response = await fetch('/api/edit_profile',{
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                 body: JSON.stringify({profile: {bio, location, website}})
            });

          const data = await response.json();

            if(response.status === 200){
                alert("Profile Edited");
                 await fetchCurrentUser();
                  hideAllSections();
              } else {
                alert(data.error || 'Failed to edit profile');
            }
       }
       // Function to create a new post
       async function createPost() {
            if (!currentUserId) {
               alert('Please login and enter post content.');
               return;
           }

           const content = document.getElementById('post-content').value;
           if (!content) {
               alert('Please enter post content.');
               return;
           }

           const response = await fetch('/api/create_post', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ content, user_id: currentUserId })
           });

           const data = await response.json();
           if (response.status === 201) {
               document.getElementById('post-content').value = ''; // Clear the textarea
               loadPosts(); // Reload posts after creating a new one
           } else {
               alert(data.error || 'Failed to create post.');
           }
       }

       // Function to retweet a post
        async function retweetPost() {
           if (!currentUserId) {
               alert('Please login to retweet.');
               return;
           }
            const originalPostId = prompt("Enter the ID of the post you want to retweet:");
           if (!originalPostId) {
               alert('Please provide a valid post ID.');
               return;
           }
           const response = await fetch('/api/retweet', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ user_id: currentUserId, original_post_id: originalPostId })
           });

           const data = await response.json();
           if (response.status === 201) {
               loadPosts(); // Reload posts after retweeting
           } else {
               alert(data.error || 'Failed to retweet post.');
           }
       }

       // Function to quote tweet a post
       async function quoteTweet() {
             if (!currentUserId) {
               alert('Please login to quote tweet.');
               return;
           }
           const originalPostId = prompt("Enter the ID of the post you want to quote:");
           const quotedContent = prompt("Enter your comment:");
           if (!originalPostId || !quotedContent) {
               alert('Please provide valid inputs.');
               return;
           }

           const response = await fetch('/api/quote_tweet', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ user_id: currentUserId, original_post_id: originalPostId, quoted_content: quotedContent })
           });

           const data = await response.json();
           if (response.status === 201) {
               loadPosts(); // Reload posts after quote tweeting
           } else {
               alert(data.error || 'Failed to create quote tweet.');
           }
       }

       // Function to load and display posts
       async function loadPosts() {
           let apiUrl =  '/api/get_posts'
           if(!currentUserId){
              apiUrl = '/api/get_guest_posts'
            }
           const response = await fetch(apiUrl);
           const posts = await response.json();
            const postsContainer = document.getElementById('posts-container');
           postsContainer.innerHTML = ''; // Clear existing posts

           posts.forEach(post => {
               const postElement = document.createElement('div');
               postElement.className = 'post';
               postElement.innerHTML = `
                   <p>${post.content}</p>
                   <small>Posted by ${post.user_id} at ${post.timestamp}</small>
                  ${currentUserId ?
                       `
                          <div class="post-actions">
                            <button onclick="likePost('${post.id}')"><i class="fas fa-heart"></i> Like (${post.likes})</button>
                            <button onclick="replyToPost('${post.id}')"><i class="fas fa-reply"></i> Reply</button>
                            <button onclick="bookmarkPost('${post.id}')"><i class="fas fa-bookmark"></i> Bookmark</button>
                            </div>` : ''
                       }
               `;
               postsContainer.appendChild(postElement);
           });
       }
         // Function to view guest post
       async function viewGuestPost() {
           await loadPosts();
         }

       // Function to like a post
       async function likePost(postId) {
           if (!currentUserId) {
               alert('Please login to like posts.');
               return;
           }

           const response = await fetch('/api/like_post', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ post_id: postId, user_id: currentUserId })
           });

           const data = await response.json();
           if (response.status === 200) {
               loadPosts(); // Reload posts to update like count
           } else {
               alert(data.error || 'Failed to like post.');
           }
       }

       // Function to reply to a post
       async function replyToPost(postId) {
           const replyContent = prompt("Enter your reply:");
           if (!replyContent || !currentUserId) {
               alert('Please login and enter reply content.');
               return;
           }

           const response = await fetch('/api/reply', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ user_id: currentUserId, original_post_id: postId, content: replyContent })
           });

           const data = await response.json();
           if (response.status === 201) {
               loadPosts(); // Reload posts after replying
           } else {
               alert(data.error || 'Failed to reply to post.');
           }
       }

       // Function to load and display direct messages
       async function loadDMs() {
           const response = await fetch(`/api/get_dms`);
           const dms = await response.json();

           const dmsContainer = document.getElementById('dms-container');
           dmsContainer.innerHTML = ''; // Clear existing DMs

           dms.forEach(dm => {
               const dmElement = document.createElement('div');
               dmElement.className = 'dm';
               dmElement.innerHTML = `
                   <p>${dm.content}</p>
                   <small>From ${dm.sender_id} at ${dm.timestamp}</small>
               `;
               dmsContainer.appendChild(dmElement);
           });
       }

        // Function to send a direct message
       async function sendDM() {
           const receiverUsername = document.getElementById('dm-receiver').value;
           const content = document.getElementById('dm-content').value;

            if (!receiverUsername || !content || !currentUserId) {
               alert('Please login and provide valid inputs.');
               return;
           }

           const response = await fetch('/api/send_dm', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ receiver_username: receiverUsername, content })
           });

           const data = await response.json();
           if (response.status === 201) {
               document.getElementById('dm-content').value = ''; // Clear the textarea
               loadDMs(); // Reload DMs after sending
           } else {
               alert(data.error || 'Failed to send DM.');
           }
       }
       // Function to load and display trending topics
        async function loadTrendingTopics() {
           const response = await fetch('/api/trending_topics');
           const topics = await response.json();

           const topicsContainer = document.getElementById('topics-container');
           topicsContainer.innerHTML = '';

           topics.forEach(topic => {
               const topicElement = document.createElement('div');
               topicElement.className = 'topic';
               topicElement.innerHTML = `
                   <span>#${topic.name} (${topic.count})</span>
               `;
               topicsContainer.appendChild(topicElement);
           });
       }

       // Function to handle search
       async function searchPostsAndUsers() {
           const query = document.getElementById('search-query').value;
           if (!query) {
               alert('Please enter a search term.');
               return;
           }

           const response = await fetch(`/api/search?query=${query}`);
           const data = await response.json();

           const searchResults = document.getElementById('search-results');
           searchResults.innerHTML = '';

           if (data.posts.length > 0) {
             const postSection =  document.createElement('div');
               postSection.innerHTML =  `<h2> Posts </h2>`
                searchResults.appendChild(postSection);
               data.posts.forEach(post => {
                 const postElement = document.createElement('div');
                 postElement.className = 'post';
                 postElement.innerHTML = `
                   <p>${post.content}</p>
                   <small>Posted by ${post.user_id} at ${post.timestamp}</small>
                    `;
                    searchResults.appendChild(postElement);
               });
           }
          if (data.users.length > 0) {
               const userSection = document.createElement('div');
               userSection.innerHTML =  `<h2> Users </h2>`
                searchResults.appendChild(userSection);
               data.users.forEach(user => {
                  const userElement = document.createElement('div');
                  userElement.className = 'user';
                  userElement.innerHTML =  `
                    <span> @${user.username} </span>
                   `;
                    searchResults.appendChild(userElement);
               });
            }

          if(data.posts.length === 0 && data.users.length === 0) {
            const noResults = document.createElement('div');
            noResults.innerHTML = '<span>No Results</span>';
            searchResults.appendChild(noResults);
          }
        }
        // Function to bookmark a post
      async function bookmarkPost(postId) {
           if(!currentUserId){
              alert('Please login to bookmark post');
               return;
           }
           const response = await fetch('/api/bookmark_post',{
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ post_id: postId, user_id: currentUserId})
            });

            const data = await response.json();
             if (response.status === 200) {
                  alert("Post bookmarked successfully")
              }else {
                 alert(data.error || 'Failed to bookmark');
              }
      }
     // Function to get user bookmarks
      async function getBookmarks(){
           if(!currentUserId){
                alert("Please log in to view bookmarks")
               return;
           }
          const response = await fetch('/api/get_bookmarks');
           const bookmarks = await response.json();

           const bookmarksContainer = document.getElementById('bookmarks-container');
           bookmarksContainer.innerHTML = '';

           bookmarks.forEach(bookmark => {
               const bookmarkElement = document.createElement('div');
               bookmarkElement.className = 'post';
                bookmarkElement.innerHTML = `
                   <p>${bookmark.content}</p>
                   <small>Posted by ${bookmark.user_id} at ${bookmark.timestamp}</small>
                     <button onclick="removeBookmark('${bookmark.id}')"><i class="fas fa-trash"></i> Remove</button>
               `;
               bookmarksContainer.appendChild(bookmarkElement)
           })
       }
    // Function to remove bookmark
   async function removeBookmark(postId){
     if(!currentUserId){
        alert("Please Login to remove bookmark")
        return;
     }
        const response = await fetch('/api/remove_bookmark', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({post_id: postId})
           });
           const data = await response.json();
            if (response.status === 200) {
                getBookmarks();
              }else {
                 alert(data.error || 'Failed to remove bookmark');
              }
   }
   // Function to mute a user
   async function muteUser(){
        if(!currentUserId){
             alert("Please login to mute a user")
            return;
        }
          const username = document.getElementById('mute-username').value
           if(!username){
             alert("Please Enter User to mute")
              return;
           }
         const userResponse = await fetch(`/api/search?query=${username}`)
         const userData = await userResponse.json();
          if(userData.users.length === 0){
              alert("User not found to mute");
              return;
           }
        const mutedUser = userData.users[0];

          const response = await fetch('/api/mute_user', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json'},
               body: JSON.stringify({ muted_id: mutedUser.id})
           });
          const data = await response.json()
            if(response.status === 200) {
              document.getElementById('mute-username').value = '';
              loadMutedUsers();
            }else {
               alert(data.error || 'Mute failed');
            }
   }
   // Function to unmute a user
   async function unmuteUser(mutedId){
        if(!currentUserId){
            alert('Please Login to unmute a user')
           return;
       }
          const response = await fetch('/api/unmute_user', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({ muted_id: mutedId })
           })
           const data = await response.json()
             if(response.status === 200){
                loadMutedUsers();
             }else {
                alert(data.error || "Failed to unmute user");
             }
       }
   // Function to load muted users
    async function loadMutedUsers(){
         if(!currentUserId){
           return;
          }
          const response = await fetch('/api/get_muted_users');
           const data = await response.json();

           const mutedUsersContainer = document.getElementById('muted-users-container');
           mutedUsersContainer.innerHTML = '';

           if(data.mutedUsers.length === 0){
                const noMutes = document.createElement('span');
                noMutes.innerHTML = "<span>No Mutes Yet</span>";
                mutedUsersContainer.appendChild(noMutes);
                 return;
            }
           data.mutedUsers.forEach(mutedId => {
               const mutedElement = document.createElement('div');
               const unmuteBtn =  `<button onclick="unmuteUser('${mutedId}')">Unmute</button>`
              const mutedUser =  findUserById(mutedId)
               mutedElement.innerHTML = `<span>@${mutedUser.username}  ${unmuteBtn} </span>`
                mutedUsersContainer.appendChild(mutedElement)
           })
       }
   // Function to get user by Id
   function findUserById(userId){
       const  users =  [];
       const  usersString = JSON.stringify(users)
         return JSON.parse(usersString).find((user) => user.id === userId);
   }
   async function saveProfile() {
       if (!currentUserId) {
           alert("Please log in to edit profile");
           return;
       }
          const bio = document.getElementById('edit-bio').value;
          const location = document.getElementById('edit-location').value;
           const website = document.getElementById('edit-website').value;

       const profileData = {
           bio: bio,
           location: location,
           website: website,
       }

       const response = await fetch('/api/edit_profile', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({profile: profileData})
       });
       const data = await response.json();
       if(response.status === 200){
          alert("Profile Updated Successfully");
             await fetchCurrentUser();
            hideAllSections();
       } else {
         alert(data.error || 'Failed to edit profile');
       }
    }
        // Event listeners
       document.getElementById('register-button').addEventListener('click', registerUser);
       document.getElementById('login-button').addEventListener('click', loginUser);
       document.getElementById('logout-button').addEventListener('click', logoutUser);
      document.getElementById('tweet-button').addEventListener('click', () => {
         hideAllSections();
            document.getElementById('create-post').style.display = 'block';
       });
       document.getElementById('post-button').addEventListener('click', createPost);
       document.getElementById('retweet-button').addEventListener('click', retweetPost);
       document.getElementById('quote-tweet-button').addEventListener('click', quoteTweet);
       document.getElementById('send-dm-button').addEventListener('click', sendDM);
       document.getElementById('guest-posts-button').addEventListener('click', viewGuestPost);
       document.getElementById('search-button').addEventListener('click', searchPostsAndUsers);
       document.getElementById('mute-button').addEventListener('click', muteUser);
       document.getElementById('edit-profile-button').addEventListener('click', saveProfile);


     // Menu Buttons
        document.getElementById('timeline-menu-button').addEventListener('click', () => {
          hideAllSections();
             document.getElementById('timeline').style.display = 'block';
             loadPosts()
        })
      document.getElementById('trending-menu-button').addEventListener('click', () => {
           hideAllSections();
            document.getElementById('trending-topics').style.display = 'block';
             loadTrendingTopics();
         });
       document.getElementById('search-menu-button').addEventListener('click', () => {
             hideAllSections();
            document.getElementById('search-section').style.display = 'block';
       })
         document.getElementById('bookmarks-menu-button').addEventListener('click', () => {
             hideAllSections()
            document.getElementById('bookmarks-section').style.display = 'block';
             getBookmarks()
         });
       document.getElementById('mute-menu-button').addEventListener('click', () => {
              hideAllSections()
              document.getElementById('mute-section').style.display = 'block'
              loadMutedUsers();
          })
        document.getElementById('spaces-menu-button').addEventListener('click', () => {
            hideAllSections()
            document.getElementById('spaces-section').style.display = 'block';
        });
         document.getElementById('edit-profile-menu-button').addEventListener('click', () => {
             hideAllSections()
             document.getElementById('edit-profile-section').style.display = 'block'
        });
        document.getElementById('moments-menu-button').addEventListener('click', () => {
             hideAllSections()
           document.getElementById('moments-section').style.display = 'block';
        });
       document.getElementById('analytics-menu-button').addEventListener('click', () => {
              hideAllSections()
           document.getElementById('analytics-section').style.display = 'block';
       });
        document.getElementById('polls-menu-button').addEventListener('click', () => {
            hideAllSections()
           document.getElementById('polls-section').style.display = 'block';
       });
       document.getElementById('notifications-menu-button').addEventListener('click', () => {
          hideAllSections()
            document.getElementById('notifications-section').style.display = 'block';
        });
    document.getElementById('direct-messages-menu-button').addEventListener('click', () => {
          hideAllSections()
            document.getElementById('direct-messages').style.display = 'block';
             loadDMs();
        });
       // Load posts and DMs on page load (if user is already logged in)
       window.onload = () => {
           fetchCurrentUser(); //Load user if session exist
           document.getElementById('user-section').style.display =  currentUserId ? 'none' : 'block';

       };