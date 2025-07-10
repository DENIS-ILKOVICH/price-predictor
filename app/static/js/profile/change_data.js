const settingsBtn = document.getElementById("settings-btn");
const modal = document.getElementById("change-data-modal");
const settingBody = document.getElementById("setting-body");
let mainSettingsHTML = '';

settingsBtn.addEventListener("click", () => {
  fetch("/get_user")
    .then(response => response.json())
    .then(data => {

      const user = data[0];
      mainSettingsHTML = `
  <h3>Settings</h3><span class="close-setting" onclick="closeSettingModal()">&times;</span>
  <br>
  <div class="header">
    <div class="profile-avatar">
      <img src="${user.image}" alt="Profile Image" class="avatar-img">
    </div>
    <div class="profile-name">
      <h3>${user.name}</h3>
      <button class="change-btn" onclick="changeUsername()">Change Name</button>
    </div>
  </div>

  <div class="user-data">
    <div class="info-item">
      <strong>Email:</strong> ${user.email}
      <button onclick="changeEmail()">Change</button>
    </div>
    <div class="info-item">
      <strong>Password:</strong> ***************
      <button onclick="changePassword()">Change</button>
    </div>
  </div>
`;
      settingBody.innerHTML = mainSettingsHTML;
      modal.style.display = "flex";
    })
    .catch(err => {
      settingBody.innerHTML = "<p>Error retrieving user data.</p>";
      modal.style.display = "flex";
    });
});

function closeSettingModal() {
  modal.style.display = "none";
}

function editField(field) {
  let newValue = prompt(`Enter new value for ${field}:`);
  if (newValue) {
    fetch(`/update_user`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ field, value: newValue })
    })
    .then(res => res.json())
    .then(res => {
      alert(res.message || "Successfully updated!");
      closeSettingModal();
    })
    .catch(() => alert("Error while updating."));
  }
}

function renderMainSettings() {
  settingBody.innerHTML = mainSettingsHTML;
}

function changeEmail() {
  fetch("/change_email", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "true" })
  })
  .then(response => response.json())
  .then(res => {
    if (res.message === "Code created") {

      settingBody.innerHTML = `
  <div class="back-button" onclick="renderMainSettings()" style="cursor:pointer;"><</div>
  <h3>Enter the verification code</h3>
  <input class="code-input" type="text" id="confirmation-code" placeholder="Enter code">
  <div id="email-update-message" class="message-box" style="display:none;"></div>
  <div class="button-block">
    <button class="save-username-btn" id="verify-code-btn">Verify Code</button>
  </div>
`;

      document.getElementById("verify-code-btn").addEventListener("click", verifyCode);
      toastr.success("Verification code has been sent to your email.");
    } else {
      toastr.error("Failed to send the verification code.");
    }
  })
  .catch(() => toastr.error("Error while requesting the code."));
}

function verifyCode() {
  const code = document.getElementById("confirmation-code").value.trim();
  const button = document.getElementById("verify-code-btn");
  const msgBox = document.getElementById("email-update-message");

  if (!code) {
    showEmailMessage("error", "Please enter the code.");
    return;
  }

  button.disabled = true;

  const errorTranslations = {
    "Invalid code value": "Invalid code."
  };

  fetch("/change_email", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "verify", code })
  })
    .then(async (response) => {
      const res = await response.json();

      if (!response.ok) {
        const translatedMessage = errorTranslations[res.error] || "Verification error.";
        throw new Error(translatedMessage);
      }

      return res;
    })
    .then((res) => {
      showEmailMessage("success", "Code verified successfully!");
      setTimeout(() => {
        settingBody.innerHTML = `
  <div class="back-button" onclick="renderMainSettings()" style="cursor:pointer;"><</div>
  <h3>Enter current password and new email</h3>
  <input class="password-input" type="password" id="current-password" placeholder="Current password">
  <input class="email-input" type="email" id="new-email" placeholder="New email address">
  <div id="email-update-message" class="message-box" style="display:none;"></div>
  <div class="button-block">
    <button class="save-username-btn" id="update-email-btn">Update Email</button>
  </div>
`;

        document.getElementById("update-email-btn").addEventListener("click", updateEmail);
      }, 1500);
    })
    .catch((err) => {
      showEmailMessage("error", err.message || "Server unavailable or an error occurred.");
      button.disabled = false;
    });
}

function showEmailMessage(type, text) {
  const msgBox = document.getElementById("email-update-message");
  if (!msgBox) return;
  msgBox.className = `message-box ${type}`;
  msgBox.textContent = text;
  msgBox.style.display = "block";
}

function updateEmail() {
  const password = document.getElementById("current-password").value.trim();
  const newEmail = document.getElementById("new-email").value.trim();

  if (!password || !newEmail) {
    showEmailMessage("error", "Please fill in all fields.");
    return;
  }

  const errorTranslations = {
    "Invalid input data": "Invalid request format.",
    "Empty JSON body": "Empty request body.",
    "Invalid input action": "Invalid action parameter.",
    "Invalid input code verify": "Missing verification code.",
    "Wrong password": "Incorrect password.",
    "Missing email": "New email is required.",
    "Invalid email format": "Invalid email format.",
    "Email already in use": "This email is already in use.",
    "Data processing error": "Data processing error. Please try again later.",
    "Internal server error": "Internal server error. Please try again later."
  };

  fetch("/change_email", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "update", password, email: newEmail })
  })
    .then(async (response) => {
      const res = await response.json();

      if (!response.ok) {
        const translatedMessage = errorTranslations[res.error] || "Failed to update email.";
        throw new Error(translatedMessage);
      }

      return res;
    })
    .then((res) => {
      toastr.success("Email updated successfully!");
      setTimeout(() => {
        closeSettingModal();
        location.reload();
      }, 1500);
    })
    .catch((err) => {
      showEmailMessage("error", err.message || "Server unavailable or an error occurred.");
    });
}

function changeUsername() {
  settingBody.innerHTML = `
  <div class="back-button" onclick="renderMainSettings()" style="cursor:pointer;"><</div>
  <h3>Change Username</h3>
  <input type="text" id="new-username" placeholder="New username"><br>
  <div id="username-update-message" class="message-box" style="display: none;"></div>
  <div class="button-block">
    <button class='save-username-btn' id="save-username-btn">Save</button>
    <button class='close-b-btn' onclick="closeSettingModal()">Cancel</button>
  </div>
`;

  function showUsernameMessage(type, text) {
    const msgBox = document.getElementById("username-update-message");
    if (!msgBox) return;
    msgBox.className = `message-box ${type}`;
    msgBox.textContent = text;
    msgBox.style.display = "block";
  }

  const errorTranslations = {
    "Invalid input data": "Invalid request format.",
    "Empty JSON body": "Empty request body.",
    "Username is required": "Please enter a username.",
    "The name must contain at least 2 characters.": "Username too short.",
    "The name must contain no more than 15 characters.": "Username must be no more than 15 characters.",
    "The name may contain only letters, numbers, or the underscore '_' character.": "Username can only contain letters, numbers, or underscores.",
    "Internal server error": "Internal server error. Please try again later.",
    "Username successfully changed": "Username changed successfully!"
  };

  document.getElementById("save-username-btn").addEventListener("click", () => {
    const newUsername = document.getElementById("new-username").value.trim();

    if (!newUsername) {
      showUsernameMessage("error", "Please enter a new username.");
      return;
    }

    fetch("/change_username", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: newUsername })
    })
    .then(async (response) => {
      const res = await response.json();
      if (!response.ok) {
        const translated = errorTranslations[res.error] || "Error while changing username.";
        throw new Error(translated);
      }
      return res;
    })
    .then((res) => {
      toastr.success(errorTranslations[res.message] || "Username changed successfully!");
      setTimeout(() => {
        closeSettingModal();
        location.reload();
      }, 1500);
    })
    .catch((err) => {
      showUsernameMessage("error", err.message || "Server unavailable or an error occurred.");
    });
  });
}

function changePassword() {
  settingBody.innerHTML = `
    <div class="back-button" onclick="renderMainSettings()" style="cursor:pointer;"><</div>
    <h3>Change Password</h3>
    <input class="password-input" type="password" id="old-password" placeholder="Current password"><br>
    <input class="password-input" type="password" id="new-password" placeholder="New password"><br>
    <input class="password-input" type="password" id="repeat-password" placeholder="Repeat new password"><br>
    <div id="password-update-message" class="message-box" style="display: none;"></div>
    <div class="button-block">
    <button class='save-username-btn' id="submit-password-change">Change Password</button>
    <button class='close-b-btn' onclick="closeSettingModal()">Cancel</button>
    </div>
  `;

  function showPasswordMessage(type, text) {
    const msgBox = document.getElementById("password-update-message");
    if (!msgBox) return;
    msgBox.className = `message-box ${type}`;
    msgBox.textContent = text;
    msgBox.style.display = "block";
  }

  const errorTranslations = {
    "Invalid input data": "Invalid request format.",
    "Empty JSON body": "Empty request body.",
    "Old password is required": "Current password is required.",
    "New password is required": "New password is required.",
    "Repeat password is required": "Please confirm the new password.",
    "Passwords don't match": "Passwords do not match.",
    "Wrong password": "Incorrect current password.",
    "The password must contain at least 6 characters.": "Password must be at least 6 characters long.",
    "Passwords do not match.": "Passwords do not match.",
    "The password must contain both letters and numbers.": "Password must include both letters and numbers."
  };

  document.getElementById("submit-password-change").addEventListener("click", () => {
    const oldPassword = document.getElementById("old-password").value.trim();
    const newPassword = document.getElementById("new-password").value.trim();
    const repeatPassword = document.getElementById("repeat-password").value.trim();

    if (!oldPassword || !newPassword || !repeatPassword) {
      showPasswordMessage("error", "Please complete all fields.");
      return;
    }

    fetch("/change_password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword,
        new_password_repeat: repeatPassword
      })
    })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      if (status === 201) {
        toastr.success("Password successfully changed!");
        setTimeout(() => {
          closeSettingModal();
        }, 1500);
      } else {
        const translatedMessage = errorTranslations[body.error] || "Error updating password.";
        showPasswordMessage("error", translatedMessage);
      }
    })
    .catch(() => {
      showPasswordMessage("error", "Internal server error while updating password.");
    });
  });
}
