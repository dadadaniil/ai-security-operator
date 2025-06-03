package com.sdc.service.mapper;

import com.sdc.model.Tag;
import com.sdc.model.Task;
import com.sdc.model.dto.TaskDto;
import com.sdc.repository.TagRepository;
import com.sdc.repository.TaskTypeRepository;
import com.sdc.repository.UserRepository;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.Set;
import java.util.stream.Collectors;

@Component
public class TaskMapper {
    private final TaskTypeRepository taskTypeRepository;
    private final UserRepository userRepository;
    private final TagRepository tagRepository;
    private final UserToCreatorMapper userToCreatorMapper;

    public TaskMapper(
        TaskTypeRepository taskTypeRepository,
        UserRepository userRepository,
        TagRepository tagRepository,
        UserToCreatorMapper userToCreatorMapper
    ) {
        this.taskTypeRepository = taskTypeRepository;
        this.userRepository = userRepository;
        this.tagRepository = tagRepository;
        this.userToCreatorMapper = userToCreatorMapper;
    }

    public Task taskDtoToEntity(TaskDto taskDto) {
        Task task = new Task(
            taskDto.getTitle(),
            taskDto.getDescription(),
            taskDto.getPaymentAmount(),
            taskDto.getCreatorPublicContacts(),
            taskDto.getDeadline()
        );

        task.setCreator(userRepository.getReferenceById(taskDto.getCreator().getId()));
        task.setType(taskTypeRepository.getReferenceById(taskDto.getType().getId()));

        Set<Long> tagIds = taskDto.getTags().stream()
            .map(Tag::getId)
            .collect(Collectors.toSet());

        Set<Tag> tags = tagRepository.findByIdIn(tagIds);
        task.setTags(tags);
        return task;
    }

    public TaskDto taskEntityToDto(Task task) {
        TaskDto taskDto = new TaskDto();
        taskDto.setId(task.getId());
        taskDto.setTitle(task.getTitle());
        taskDto.setDescription(task.getDescription());
        taskDto.setPaymentAmount(task.getBudget());
        taskDto.setCreatorPublicContacts(task.getContacts());
        taskDto.setTags(new ArrayList<>(task.getTags()));
        taskDto.setType(task.getType());
        taskDto.setCreatedAt(task.getCreatedDate());
        taskDto.setDeadline(task.getExpectedDeliveryTime());

        taskDto.setCreator(userToCreatorMapper.userToUserViewDto(task.getCreator()));
        return taskDto;
    }
}
