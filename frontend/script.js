// =========================================================
// APPLICATION STATE
// =========================================================


// Currently logged-in user.
let currentUser = "";


// Currently selected private-chat user.
let selectedPrivateUser = null;


// Currently selected room.
let selectedRoom = null;


// Demo users.
// These will later come from the backend.
const users = [

    {
        username: "Alice",
        email: "alice@example.com"
    },

    {
        username: "Bob",
        email: "bob@example.com"
    },

    {
        username: "Charlie",
        email: "charlie@example.com"
    },

    {
        username: "David",
        email: "david@example.com"
    }

];


// Demo rooms.
let rooms = [

    {
        name: "Friends",
        code: "398612",
        owner: "Alice",
        members: [
            "Alice",
            "Bob"
        ]
    },

    {
        name: "College",
        code: "583214",
        owner: "Alice",
        members: [
            "Alice",
            "Charlie"
        ]
    }

];


// Demo private messages.
const privateMessages = {};


// Demo room messages.
const roomMessages = {};


// =========================================================
// ELEMENTS
// =========================================================


// Authentication.

const authScreen =
    document.getElementById(
        "authScreen"
    );

const loginTab =
    document.getElementById(
        "loginTab"
    );

const registerTab =
    document.getElementById(
        "registerTab"
    );

const loginForm =
    document.getElementById(
        "loginForm"
    );

const registerForm =
    document.getElementById(
        "registerForm"
    );

const authMessage =
    document.getElementById(
        "authMessage"
    );


// Application.

const appScreen =
    document.getElementById(
        "appScreen"
    );


// Navigation.

const homeNav =
    document.getElementById(
        "homeNav"
    );

const privateNav =
    document.getElementById(
        "privateNav"
    );

const roomsNav =
    document.getElementById(
        "roomsNav"
    );


// Pages.

const homePage =
    document.getElementById(
        "homePage"
    );

const privatePage =
    document.getElementById(
        "privatePage"
    );

const privateChatPage =
    document.getElementById(
        "privateChatPage"
    );

const roomsPage =
    document.getElementById(
        "roomsPage"
    );

const roomChatPage =
    document.getElementById(
        "roomChatPage"
    );


// Home.

const homeWelcome =
    document.getElementById(
        "homeWelcome"
    );

const homePrivateButton =
    document.getElementById(
        "homePrivateButton"
    );

const homeRoomButton =
    document.getElementById(
        "homeRoomButton"
    );


// Sidebar.

const sidebarUsername =
    document.getElementById(
        "sidebarUsername"
    );

const sidebarAvatar =
    document.getElementById(
        "sidebarAvatar"
    );

const logoutButton =
    document.getElementById(
        "logoutButton"
    );


// User search.

const userSearch =
    document.getElementById(
        "userSearch"
    );

const userList =
    document.getElementById(
        "userList"
    );

const userEmpty =
    document.getElementById(
        "userEmpty"
    );

const userCount =
    document.getElementById(
        "userCount"
    );


// Private conversation.

const privateChatBack =
    document.getElementById(
        "privateChatBack"
    );

const privateChatAvatar =
    document.getElementById(
        "privateChatAvatar"
    );

const privateChatName =
    document.getElementById(
        "privateChatName"
    );

const privateMessagesElement =
    document.getElementById(
        "privateMessages"
    );

const privateMessageForm =
    document.getElementById(
        "privateMessageForm"
    );

const privateMessageInput =
    document.getElementById(
        "privateMessageInput"
    );


// Rooms.

const createRoomForm =
    document.getElementById(
        "createRoomForm"
    );

const joinRoomForm =
    document.getElementById(
        "joinRoomForm"
    );

const roomNameInput =
    document.getElementById(
        "roomNameInput"
    );

const roomCodeInput =
    document.getElementById(
        "roomCodeInput"
    );

const roomList =
    document.getElementById(
        "roomList"
    );


// Room conversation.

const roomChatBack =
    document.getElementById(
        "roomChatBack"
    );

const roomChatName =
    document.getElementById(
        "roomChatName"
    );

const roomChatCode =
    document.getElementById(
        "roomChatCode"
    );

const roomMessagesElement =
    document.getElementById(
        "roomMessages"
    );

const roomMessageForm =
    document.getElementById(
        "roomMessageForm"
    );

const roomMessageInput =
    document.getElementById(
        "roomMessageInput"
    );


// Members modal.

const membersModal =
    document.getElementById(
        "membersModal"
    );

const membersList =
    document.getElementById(
        "membersList"
    );

const roomMembersButton =
    document.getElementById(
        "roomMembersButton"
    );

const closeMembersModal =
    document.getElementById(
        "closeMembersModal"
    );


// =========================================================
// AUTH TABS
// =========================================================


loginTab.addEventListener(
    "click",
    function () {

        loginTab.classList.add(
            "active"
        );

        registerTab.classList.remove(
            "active"
        );

        loginForm.classList.remove(
            "hidden"
        );

        registerForm.classList.add(
            "hidden"
        );

        authMessage.textContent = "";

    }
);


registerTab.addEventListener(
    "click",
    function () {

        registerTab.classList.add(
            "active"
        );

        loginTab.classList.remove(
            "active"
        );

        registerForm.classList.remove(
            "hidden"
        );

        loginForm.classList.add(
            "hidden"
        );

        authMessage.textContent = "";

    }
);


// =========================================================
// LOGIN
// =========================================================


loginForm.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();


        const username =
            document.getElementById(
                "loginUsername"
            ).value.trim();


        const password =
            document.getElementById(
                "loginPassword"
            ).value;


        if (
            username.length === 0
            ||
            password.length === 0
        ) {

            authMessage.textContent =
                "Please enter username and password.";

            return;
        }


       fetch("http://127.0.0.1:8000/api/login", {
    method: "POST",

    headers: {
        "Content-Type": "application/json"
    },

    body: JSON.stringify({
        username: username,
        password: password
    })
})
.then(function (response) {
    return response.json();
})
.then(function (data) {

    if (data.success) {

        loginUser(
            data.username
        );

    } else {

        authMessage.textContent =
            data.message;

    }

})
.catch(function () {

    authMessage.textContent =
        "Unable to connect to CipherChat server.";

});

    }
);


// =========================================================
// REGISTER
// =========================================================


registerForm.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();


        const username =
            document.getElementById(
                "registerUsername"
            ).value.trim();


        const email =
            document.getElementById(
                "registerEmail"
            ).value.trim();


        const password =
            document.getElementById(
                "registerPassword"
            ).value;


        if (
            username.length === 0
            ||
            email.length === 0
            ||
            password.length === 0
        ) {

            authMessage.textContent =
                "Please complete all fields.";

            return;
        }


        


       fetch("http://127.0.0.1:8000/api/register", {
    method: "POST",

    headers: {
        "Content-Type": "application/json"
    },

    body: JSON.stringify({
        username: username,
        email: email,
        password: password
    })
})
.then(function (response) {
    return response.json();
})
.then(function (data) {

    if (data.success) {

        loginUser(
            username
        );

    } else {

        authMessage.textContent =
            data.message;

    }

})
.catch(function () {

    authMessage.textContent =
        "Unable to connect to CipherChat server.";

});

    }
);


// =========================================================
// LOGIN USER
// =========================================================


function loginUser(username) {

    currentUser = username;


    // Update sidebar.
    sidebarUsername.textContent =
        username;


    sidebarAvatar.textContent =
        username
            .charAt(0)
            .toUpperCase();


    // Update home.
    homeWelcome.textContent =
        "Welcome back, "
        + username
        + ".";


    // Show application.
    authScreen.classList.add(
        "hidden"
    );

    appScreen.classList.remove(
        "hidden"
    );


    showPage(
        homePage,
        homeNav
    );

}


// =========================================================
// LOGOUT
// =========================================================


logoutButton.addEventListener(
    "click",
    function () {

        currentUser = "";

        selectedPrivateUser = null;

        selectedRoom = null;


        appScreen.classList.add(
            "hidden"
        );

        authScreen.classList.remove(
            "hidden"
        );


        loginForm.reset();

        registerForm.reset();


        authMessage.textContent = "";


        loginTab.click();

    }
);


// =========================================================
// PAGE NAVIGATION
// =========================================================


function hideAllPages() {

    homePage.classList.add(
        "hidden"
    );

    privatePage.classList.add(
        "hidden"
    );

    privateChatPage.classList.add(
        "hidden"
    );

    roomsPage.classList.add(
        "hidden"
    );

    roomChatPage.classList.add(
        "hidden"
    );


    homeNav.classList.remove(
        "active"
    );

    privateNav.classList.remove(
        "active"
    );

    roomsNav.classList.remove(
        "active"
    );

}


function showPage(page, navButton) {

    hideAllPages();


    page.classList.remove(
        "hidden"
    );


    if (navButton) {

        navButton.classList.add(
            "active"
        );

    }

}


// Home navigation.

homeNav.addEventListener(
    "click",
    function () {

        showPage(
            homePage,
            homeNav
        );

    }
);


// Private navigation.

privateNav.addEventListener(
    "click",
    function () {

        showPage(
            privatePage,
            privateNav
        );

        renderUsers();

    }
);


// Room navigation.

roomsNav.addEventListener(
    "click",
    function () {

        showPage(
            roomsPage,
            roomsNav
        );

        renderRooms();

    }
);


// Home private button.

homePrivateButton.addEventListener(
    "click",
    function () {

        showPage(
            privatePage,
            privateNav
        );

        renderUsers();

    }
);


// Home room button.

homeRoomButton.addEventListener(
    "click",
    function () {

        showPage(
            roomsPage,
            roomsNav
        );

        renderRooms();

    }
);


// =========================================================
// USER SEARCH
// =========================================================


userSearch.addEventListener(
    "input",
    function () {

        renderUsers(
            userSearch.value
        );

    }
);

async function renderUsers(searchText = "") {

    userList.innerHTML = "";

    const search =
        searchText
            .trim()
            .toLowerCase();


    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/api/users"
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load users."
            );

        }


        const users =
            await response.json();


        const filteredUsers =
            users.filter(
                function (user) {

                    // Never show current user.
                    if (
                        user.username
                            .toLowerCase()
                        ===
                        currentUser
                            .toLowerCase()
                    ) {

                        return false;
                    }


                    return (
                        user.username
                            .toLowerCase()
                            .includes(search)
                        ||
                        user.email
                            .toLowerCase()
                            .includes(search)
                    );

                }
            );


        userCount.textContent =
            filteredUsers.length
            + " users";


        if (
            filteredUsers.length === 0
        ) {

            userEmpty.classList.remove(
                "hidden"
            );

            return;

        }


        userEmpty.classList.add(
            "hidden"
        );


        filteredUsers.forEach(
            function (user) {

                const row =
                    document.createElement(
                        "button"
                    );


                row.type = "button";

                row.className =
                    "user-row";


                const avatar =
                    document.createElement(
                        "div"
                    );


                avatar.className =
                    "user-avatar";


                avatar.textContent =
                    user.username
                        .charAt(0)
                        .toUpperCase();


                const details =
                    document.createElement(
                        "div"
                    );


                details.className =
                    "user-details";


                const name =
                    document.createElement(
                        "strong"
                    );


                name.textContent =
                    user.username;


                const email =
                    document.createElement(
                        "small"
                    );


                email.textContent =
                    user.email;


                const online =
                    document.createElement(
                        "span"
                    );


                online.className =
                    "online-dot";


                details.appendChild(
                    name
                );

                details.appendChild(
                    email
                );


                row.appendChild(
                    avatar
                );

                row.appendChild(
                    details
                );

                row.appendChild(
                    online
                );


                row.addEventListener(
                    "click",
                    function () {

                        openPrivateChat(
                            user
                        );

                    }
                );


                userList.appendChild(
                    row
                );

            }
        );

    } catch (error) {

        userCount.textContent =
            "0 users";

        userEmpty.classList.remove(
            "hidden"
        );

    }

}


// =========================================================
// PRIVATE CHAT
// =========================================================


function openPrivateChat(user) {

    selectedPrivateUser =
        user;


    privateChatName.textContent =
        user.username;


    privateChatAvatar.textContent =
        user.username
            .charAt(0)
            .toUpperCase();


    showPage(
        privateChatPage,
        null
    );


    renderPrivateMessages();

    privateMessageInput.focus();

}


async function renderPrivateMessages() {

    privateMessagesElement.innerHTML = "";


    if (!selectedPrivateUser) {

        return;

    }


    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/api/private-messages"
                + "?username="
                + encodeURIComponent(currentUser)
                + "&other_username="
                + encodeURIComponent(
                    selectedPrivateUser.username
                )
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load messages."
            );

        }


        const data =
            await response.json();


        if (!data.success) {

            return;

        }


        data.messages.forEach(
            function (message) {

                addMessageBubble(
                    privateMessagesElement,
                    {
                        sender: message.sender,
                        text: message.text,
                        time: new Date(
                            message.time
                        ).toLocaleTimeString(
                            [],
                            {
                                hour: "2-digit",
                                minute: "2-digit"
                            }
                        )
                    }
                );

            }
        );


        scrollMessages(
            privateMessagesElement
        );


    } catch (error) {

        privateMessagesElement.innerHTML = "";

        const errorMessage =
            document.createElement("div");


        errorMessage.className =
            "empty-state";


        errorMessage.textContent =
            "Unable to load messages.";


        privateMessagesElement.appendChild(
            errorMessage
        );

    }

}

function getPrivateChatKey(
    userA,
    userB
) {

    return [
        userA,
        userB
    ]
        .sort()
        .join(":");

}


// =========================================================
// PRIVATE MESSAGE SEND
// =========================================================


privateMessageForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        if (!selectedPrivateUser) {

            return;

        }


        const text =
            privateMessageInput
                .value
                .trim();


        if (text.length === 0) {

            return;

        }


        try {

            const response =
                await fetch(
                    "http://127.0.0.1:8000/api/private-messages",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            sender: currentUser,
                            receiver:
                                selectedPrivateUser.username,
                            message: text
                        })
                    }
                );


            const data =
                await response.json();


            if (!response.ok || !data.success) {

                alert(
                    data.message
                    || "Message could not be sent."
                );

                return;

            }


            privateMessageInput.value = "";


            // Reload the conversation from SQLite.
            await renderPrivateMessages();


            privateMessageInput.focus();


        } catch (error) {

            alert(
                "Unable to connect to CipherChat server."
            );

        }

    }
);



// Back from private chat.

privateChatBack.addEventListener(
    "click",
    function () {

        showPage(
            privatePage,
            privateNav
        );

        renderUsers();

    }
);


// =========================================================
// ROOM CREATION
// =========================================================

createRoomForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();

        const roomName =
            roomNameInput
                .value
                .trim();

        if (
            roomName.length === 0
        ) {

            return;

        }

        try {

            const response =
                await fetch(
                    "http://127.0.0.1:8000/api/rooms",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            username: currentUser,
                            room_name: roomName,
                            room_type: "group"
                        })
                    }
                );

            const data =
                await response.json();

            if (!response.ok || !data.success) {

                alert(
                    data.message
                    || "Room could not be created."
                );

                return;
            }

            const room = {
                name: roomName,
                code: data.room_code,
                owner: currentUser,
                members: [
                    currentUser
                ]
            };

            rooms.push(
                room
            );

            roomNameInput.value = "";

            renderRooms();

            openRoom(
                room
            );

        } catch (error) {

            alert(
                "Unable to connect to CipherChat server."
            );

        }

    }
);


// =========================================================
// ROOM JOIN
// =========================================================


joinRoomForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();

        const code =
            roomCodeInput
                .value
                .trim();

        if (
            !/^\d{6}$/.test(code)
        ) {

            return;

        }

        try {

            const response =
                await fetch(
                    "http://127.0.0.1:8000/api/rooms/join",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            username: currentUser,
                            room_code: code
                        })
                    }
                );

            const data =
                await response.json();

            if (!response.ok || !data.success) {

                alert(
                    data.message
                    || "Unable to join room."
                );

                return;
            }

            const roomResponse =
                await fetch(
                    "http://127.0.0.1:8000/api/rooms/"
                    + code
                );

            const roomData =
                await roomResponse.json();

            if (!roomResponse.ok || !roomData.success) {

                alert(
                    "Unable to load room details."
                );

                return;
            }

            const room = {
                name: roomData.room.name,
                code: roomData.room.code,
                owner: currentUser,
                members:
                    roomData.room.members.map(
                        function (member) {
                            return member.username;
                        }
                    )
            };

            rooms = rooms.filter(
                function (item) {
                    return item.code !== code;
                }
            );

            rooms.push(room);

            roomCodeInput.value = "";

            renderRooms();

            openRoom(room);

        } catch (error) {

            alert(
                "Unable to connect to CipherChat server."
            );

        }

    }
);
// =========================================================
// ROOM LIST
// =========================================================


function renderRooms() {

    roomList.innerHTML =
        "";


    const userRooms =
        rooms.filter(
            function (room) {

                return room.members.includes(
                    currentUser
                );

            }
        );


    if (
        userRooms.length === 0
    ) {

        const empty =
            document.createElement(
                "div"
            );


        empty.className =
            "empty-state";


        empty.innerHTML =
            `
                <strong>No rooms yet</strong>
                <p>Create or join a room to get started.</p>
            `;


        roomList.appendChild(
            empty
        );


        return;

    }


    userRooms.forEach(
        function (room) {

            const row =
                document.createElement(
                    "button"
                );


            row.type = "button";

            row.className =
                "room-row";


            const icon =
                document.createElement(
                    "div"
                );


            icon.className =
                "room-row-icon";


            icon.textContent =
                "#";


            const details =
                document.createElement(
                    "div"
                );


            details.className =
                "room-details";


            const name =
                document.createElement(
                    "strong"
                );


            name.textContent =
                room.name;


            const members =
                document.createElement(
                    "small"
                );


            members.textContent =
                room.members.length
                + " members";


            const code =
                document.createElement(
                    "span"
                );


            code.className =
                "room-code";


            code.textContent =
                room.code;


            details.appendChild(
                name
            );

            details.appendChild(
                members
            );


            row.appendChild(
                icon
            );

            row.appendChild(
                details
            );

            row.appendChild(
                code
            );


            row.addEventListener(
                "click",
                function () {

                    openRoom(
                        room
                    );

                }
            );


            roomList.appendChild(
                row
            );

        }
    );

}


// =========================================================
// OPEN ROOM
// =========================================================


function openRoom(room) {

    selectedRoom =
        room;


    roomChatName.textContent =
        room.name;


    roomChatCode.textContent =
        room.code;


    showPage(
        roomChatPage,
        null
    );


    renderRoomMessages();

}


// =========================================================
// ROOM MESSAGES
// =========================================================


async function renderRoomMessages() {

    roomMessagesElement.innerHTML = "";

    if (!selectedRoom) {
        return;
    }

    const code =
        selectedRoom.code;

    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/api/rooms/"
                + encodeURIComponent(code)
                + "/messages"
            );

        const data =
            await response.json();

        if (!response.ok || !data.success) {

            return;
        }

        data.messages.forEach(
            function (message) {

                addMessageBubble(
                    roomMessagesElement,
                    {
                        sender: message.sender,
                        text: message.text,
                        time: ""
                    }
                );

            }
        );

        scrollMessages(
            roomMessagesElement
        );

    } catch (error) {

        roomMessagesElement.innerHTML = "";

        const errorMessage =
            document.createElement("div");

        errorMessage.className =
            "empty-state";

        errorMessage.textContent =
            "Unable to load messages.";

        roomMessagesElement.appendChild(
            errorMessage
        );

    }

}

// =========================================================
// ROOM MESSAGE SEND
// =========================================================


roomMessageForm.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();


        if (
            !selectedRoom
        ) {

            return;

        }


        const text =
            roomMessageInput
                .value
                .trim();


        if (
            text.length === 0
        ) {

            return;

        }


        const code =
            selectedRoom.code;


        if (
            !roomMessages[code]
        ) {

            roomMessages[code] =
                [];

        }


        roomMessages[code].push(
            {
                sender: currentUser,
                text: text,
                time: getCurrentTime()
            }
        );


        roomMessageInput.value =
            "";


        renderRoomMessages();

    }
);


// Back from room.

roomChatBack.addEventListener(
    "click",
    function () {

        showPage(
            roomsPage,
            roomsNav
        );

        renderRooms();

    }
);


// =========================================================
// MESSAGE BUBBLE
// =========================================================


function addMessageBubble(
    container,
    message
) {

    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.className =
        "message";


    if (
        message.sender
        ===
        currentUser
    ) {

        wrapper.classList.add(
            "mine"
        );

    } else {

        wrapper.classList.add(
            "other"
        );

    }


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "message-bubble";


    bubble.textContent =
        message.text;


    const time =
        document.createElement(
            "span"
        );


    time.className =
        "message-time";


    time.textContent =
        message.time;


    wrapper.appendChild(
        bubble
    );


    wrapper.appendChild(
        time
    );


    container.appendChild(
        wrapper
    );

}


// =========================================================
// ROOM MEMBERS MODAL
// =========================================================


roomMembersButton.addEventListener(
    "click",
    function () {

        if (
            !selectedRoom
        ) {

            return;

        }


        renderMembers();


        membersModal.classList.remove(
            "hidden"
        );

    }
);


function renderMembers() {

    membersList.innerHTML =
        "";


    selectedRoom.members.forEach(
        function (username) {

            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "member-row";


            const avatar =
                document.createElement(
                    "div"
                );


            avatar.className =
                "user-avatar";


            avatar.textContent =
                username
                    .charAt(0)
                    .toUpperCase();


            const info =
                document.createElement(
                    "div"
                );


            info.className =
                "member-info";


            const name =
                document.createElement(
                    "strong"
                );


            name.textContent =
                username;


            const role =
                document.createElement(
                    "small"
                );


            if (
                username
                ===
                selectedRoom.owner
            ) {

                role.textContent =
                    "Owner";

            } else {

                role.textContent =
                    "Member";

            }


            info.appendChild(
                name
            );

            info.appendChild(
                role
            );


            row.appendChild(
                avatar
            );

            row.appendChild(
                info
            );


            membersList.appendChild(
                row
            );

        }
    );

}


closeMembersModal.addEventListener(
    "click",
    function () {

        membersModal.classList.add(
            "hidden"
        );

    }
);


membersModal.addEventListener(
    "click",
    function (event) {

        if (
            event.target
            ===
            membersModal
        ) {

            membersModal.classList.add(
                "hidden"
            );

        }

    }
);


// =========================================================
// ROOM CODE GENERATOR
// =========================================================


function generateRoomCode() {

    let code;


    do {

        code =
            Math.floor(
                100000
                +
                Math.random()
                * 900000
            ).toString();


    } while (
        rooms.some(
            function (room) {

                return (
                    room.code
                    ===
                    code
                );

            }
        )
    );


    return code;

}


// =========================================================
// TIME
// =========================================================


function getCurrentTime() {

    return new Date().toLocaleTimeString(
        [],
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


// =========================================================
// SCROLL
// =========================================================


function scrollMessages(element) {

    element.scrollTop =
        element.scrollHeight;

}