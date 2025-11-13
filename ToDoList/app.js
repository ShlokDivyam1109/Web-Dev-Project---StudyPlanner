document.addEventListener('DOMContentLoaded', () => {
  const taskInput = document.getElementById("input-text");
  const addbtn = document.getElementById("add-btn");
  const taskList = document.getElementById("task-list");
  const emptyImage = document.querySelector(".empty-img");
  const taskSpace = document.querySelector(".task-space");
  const progressBar = document.getElementById("progress");
  const nums = document.getElementById("nums");


  
  // 🎉 Confetti function
  const Confetti = () => {
    const count = 200,
      defaults = { origin: { y: 0.7 } };

    function fire(particleRatio, opts) {
      confetti(
        Object.assign({}, defaults, opts, {
          particleCount: Math.floor(count * particleRatio),
        })
      );
    }

    fire(0.25, { spread: 26, startVelocity: 55 });
    fire(0.2, { spread: 60 });
    fire(0.35, { spread: 100, decay: 0.91, scalar: 0.8 });
    fire(0.1, { spread: 120, startVelocity: 25, decay: 0.92, scalar: 1.2 });
    fire(0.1, { spread: 120, startVelocity: 45 });
  };

  //  Progress bar update
  const updateP = (checkCompletion = true) => {
    const totalTasks = taskList.children.length;
    const completedTasks = taskList.querySelectorAll(".checkbox:checked").length;
    progressBar.style.width = totalTasks ? `${(completedTasks / totalTasks) * 100}%` : '0%';
    nums.textContent = `${completedTasks}/${totalTasks}`;
    if (checkCompletion && totalTasks > 0 && completedTasks === totalTasks) {
      Confetti();
    }
  };

  // Create task element in UI
  const createUIForTask = (taskText, completed = false, id = null) => {
    const li = document.createElement('li');
    li.dataset.id = id || Date.now(); // local id
    li.innerHTML = `
      <input type="checkbox" class="checkbox" ${completed ? 'checked' : ''}>
      <span>${taskText}</span>
      <div class="task-btns">
        <button class="edit-btn"><i class="fa-solid fa-pen"></i></button>
        <button class="delete-btn"><i class="fa-solid fa-trash"></i></button>
      </div>
    `;

    const checkbox = li.querySelector('.checkbox');
    const editbtn = li.querySelector('.edit-btn');
    const delbtn = li.querySelector('.delete-btn');

    if (completed) {
      li.classList.add('completed');
      editbtn.disabled = true;
      editbtn.style.opacity = "0.5";
    }

    checkbox.addEventListener('change', () => {
      const isChecked = checkbox.checked;
      li.classList.toggle('completed', isChecked);
      editbtn.disabled = isChecked;
      editbtn.style.opacity = isChecked ? "0.5" : "1";
      updateP();
    });

    editbtn.addEventListener('click', () => {
      if (!checkbox.checked) {
        taskInput.value = li.querySelector('span').textContent;
        li.remove();
        updateP(false);
      }
    });

    delbtn.addEventListener('click', () => {
      li.remove();
      updateP();
    });

    taskList.appendChild(li);
    updateP();
  };

  // Add new task
  const addTask = (text = null) => {
    const taskText = text || taskInput.value.trim();
    if (!taskText) return;
    createUIForTask(taskText, false);
    taskInput.value = "";
  };

  //  Button click + Enter key add
  addbtn.addEventListener('click', () => addTask());
  taskInput.addEventListener('keypress', (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addTask();
    }
  });

  updateP();
});
