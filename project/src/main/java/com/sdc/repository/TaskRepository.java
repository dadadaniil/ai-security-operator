package com.sdc.repository;

import com.sdc.model.Task;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TaskRepository extends JpaRepository<Task, Long> {
    Page<Task> findByAssigneesUserId(Long userId, Pageable pageable);
    Page<Task> findByCreatorUserId(Long userId, Pageable pageable);
}
