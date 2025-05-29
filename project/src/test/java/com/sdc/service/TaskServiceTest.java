package com.sdc.service;

import com.sdc.controller.configuration.auth.CustomUserDetails;
import com.sdc.model.*;
import com.sdc.model.dto.TaskDto;
import com.sdc.repository.TagRepository;
import com.sdc.repository.TaskRepository;
import com.sdc.repository.TaskTypeRepository;
import com.sdc.repository.UserRepository;
import com.sdc.service.mapper.TaskMapper;
import com.sdc.service.mapper.UserToCreatorMapper;
import com.sdc.service.pagination.PageLinksGenerator;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class TaskServiceTest {
    @Mock
    private TaskRepository taskRepository;
    @Mock
    private UserRepository userRepository;
    @Mock
    private TagRepository tagRepository;
    @Mock
    private TaskTypeRepository taskTypeRepository;
    @Mock
    private UserToCreatorMapper userToCreatorMapper;
    @InjectMocks
    private TaskMapper taskMapper;
    private TaskService taskService;

    private Task testTask;
    private Task testTask2;
    private User creator;
    private User creator2;
    private User student;

    @BeforeEach
    void beforeEach() {
        taskService = new TaskService(taskRepository, taskMapper, null, new PageLinksGenerator());

        final User creator = new User();
        creator.setUserId(1L);
        creator.setFirstName("John");
        creator.setLastName("Doe");
        creator.setEmail("john.doe@example.com");
        creator.setPassword("password");
        creator.setRole(new Role(1L, "", "", Set.of()));
        creator.setVerified(true);
        creator.setRating(5L);
        creator.setBalance(1000L);
        creator.setCreationDate(OffsetDateTime.now());
        creator.setUpdateDate(OffsetDateTime.now());
        this.creator = creator;

        final User creator2 = new User();
        creator2.setUserId(2L);
        creator2.setFirstName("John2");
        creator2.setLastName("Doe2");
        creator2.setEmail("john.doe2@example.com");
        creator2.setPassword("password");
        creator2.setRole(new Role(1L, "", "", Set.of()));
        creator2.setVerified(true);
        creator2.setRating(5L);
        creator2.setBalance(1000L);
        creator2.setCreationDate(OffsetDateTime.now());
        creator2.setUpdateDate(OffsetDateTime.now());
        this.creator2 = creator2;

        final User student = new User();
        student.setUserId(3L);
        student.setFirstName("John2");
        student.setLastName("Doe2");
        student.setEmail("john.doe2@example.com");
        student.setPassword("password");
        student.setRole(new Role(2L, "", "", Set.of()));
        student.setVerified(true);
        student.setRating(5L);
        student.setBalance(1000L);
        student.setCreationDate(OffsetDateTime.now());
        student.setUpdateDate(OffsetDateTime.now());
        this.student = student;

        final Tag tag1 = new Tag();
        tag1.setTitle("Java");

        final Tag tag2 = new Tag();
        tag2.setTitle("Spring");

        final Set<Tag> tags = new HashSet<>();
        tags.add(tag1);
        tags.add(tag2);

        final Task testTask = new Task();
        testTask.setId(1L);
        testTask.setAssignees(Set.of(student));
        testTask.setCreator(creator);
        testTask.setCreatedDate(OffsetDateTime.now());
        testTask.setTitle("Test Task");
        testTask.setDescription("This is a test task");
        testTask.setBudget(new BigDecimal("500.00"));
        testTask.setType(new TaskType(1L, "Individual", ""));
        testTask.setContacts("contact@example.com");
        testTask.setExpectedDeliveryTime(OffsetDateTime.now().plusDays(7));
        testTask.setTags(tags);
        testTask.setUpdateDate(OffsetDateTime.now());
        this.testTask = testTask;

        final Task testTask2 = new Task();
        testTask2.setId(2L);
        testTask2.setCreator(creator2);
        testTask2.setCreatedDate(OffsetDateTime.now());
        testTask2.setTitle("Test Task 2");
        testTask2.setDescription("This is a test task");
        testTask2.setBudget(new BigDecimal("500.00"));
        testTask2.setType(new TaskType(2L, "Team", ""));
        testTask2.setContacts("contact@example.com");
        testTask2.setExpectedDeliveryTime(OffsetDateTime.now().plusDays(7));
        testTask2.setTags(tags);
        testTask2.setUpdateDate(OffsetDateTime.now());
        this.testTask2 = testTask2;
    }

    @DisplayName("Test for findAllTasks()")
    @Test
    void testFindAllTasks() {
        final PageRequest pageRequest = PageRequest.of(0, 10);
        when(taskRepository.findAll(eq(pageRequest)))
            .thenReturn(new PageImpl<>(List.of(testTask)));

        final List<TaskDto> results = taskService.findAllTasks(pageRequest).getResults();

        assertEquals(1, results.size());
        assertEquals(1, results.getFirst().getId());
    }

    @DisplayName("Test for findAllCreatorsTasks()")
    @Test
    void testFindAllCreatorsTasks() {
        final PageRequest pageRequest = PageRequest.of(0, 10);
        final CustomUserDetails customUserDetails = new CustomUserDetails(creator);
        when(taskRepository.findByCreatorUserId(eq(1L), eq(pageRequest)))
            .thenReturn(new PageImpl<>(List.of(testTask)));

        final List<TaskDto> results = taskService.findAllCreatorsTasks(customUserDetails, pageRequest).getResults();

        assertEquals(1, results.size());
        assertEquals(1, results.getFirst().getId());
    }

    @DisplayName("Test for findAllImplementersTasks()")
    @Test
    void testFindAllImplementersTasks() {
        final PageRequest pageRequest = PageRequest.of(0, 10);
        final CustomUserDetails customUserDetails = new CustomUserDetails(student);
        when(taskRepository.findByAssigneesUserId(eq(3L), eq(pageRequest)))
            .thenReturn(new PageImpl<>(List.of(testTask)));

        final List<TaskDto> results = taskService.findAllImplementersTasks(customUserDetails, pageRequest).getResults();

        assertEquals(1, results.size());
        assertEquals(1, results.getFirst().getId());
    }
}
