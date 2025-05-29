package com.sdc.service.mapper;

import com.sdc.model.Tag;
import com.sdc.model.Task;
import com.sdc.model.TaskType;
import com.sdc.model.User;
import com.sdc.model.dto.TaskDto;
import com.sdc.model.dto.UserViewDto;
import com.sdc.repository.TagRepository;
import com.sdc.repository.TaskTypeRepository;
import com.sdc.repository.UserRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.Collections;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class TaskMapperTest {
    @InjectMocks
    private TaskMapper taskMapper;

    @Mock
    private UserRepository userRepository;

    @Mock
    private TaskTypeRepository taskTypeRepository;

    @Mock
    private TagRepository tagRepository;


    @DisplayName("Test for taskDtoToEntity()")
    @Test
    public void testTaskDtoToUserViewDto() {
        TaskDto taskDto = new TaskDto();
        taskDto.setTitle("Test Task");
        taskDto.setDescription("Test Description");
        taskDto.setPaymentAmount(BigDecimal.valueOf(100.0));
        taskDto.setCreatorPublicContacts("Test Contacts");
        taskDto.setDeadline(OffsetDateTime.parse("2022-12-12T12:12:12.000Z"));

        User creator = new User();
        creator.setUserId(1L);
        UserViewDto creatorDto = new UserViewDto();
        creatorDto.setId(1L);
        taskDto.setCreator(creatorDto);

        TaskType typeDto = new TaskType();
        typeDto.setId(1L);
        taskDto.setType(typeDto);

        Tag tagDto = new Tag();
        tagDto.setId(1L);
        taskDto.setTags(Collections.singletonList(tagDto));

        TaskType type = new TaskType();
        type.setId(1L);

        Tag tag = new Tag();
        tag.setId(1L);

        when(userRepository.getReferenceById(creator.getUserId())).thenReturn(creator);
        when(taskTypeRepository.getReferenceById(typeDto.getId())).thenReturn(type);
        when(tagRepository.findByIdIn(Collections.singleton(tagDto.getId()))).thenReturn(
            Collections.singleton(tag));

        Task task = taskMapper.taskDtoToEntity(taskDto);

        assertEquals(taskDto.getTitle(), task.getTitle());
        assertEquals(taskDto.getDescription(), task.getDescription());
        assertEquals(taskDto.getPaymentAmount(), task.getBudget());
        assertEquals(taskDto.getCreatorPublicContacts(), task.getContacts());
        assertEquals(taskDto.getDeadline(), task.getExpectedDeliveryTime());
        assertEquals(taskDto.getCreator().getId(), task.getCreator().getUserId());
        assertEquals(taskDto.getType().getId(), task.getType().getId());
        assertEquals(
            taskDto.getTags().stream().findFirst().orElseThrow().getId(),
            task.getTags().stream().findFirst().orElseThrow().getId()
        );
    }
}