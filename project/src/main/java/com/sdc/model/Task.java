package com.sdc.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.HashSet;
import java.util.Set;

@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter

@Entity
@Table(name = "tasks")
public class Task {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @ManyToMany(fetch = FetchType.LAZY, cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    @JoinTable(name = "assigned",
        joinColumns = @JoinColumn(name = "task_id"),
        inverseJoinColumns = @JoinColumn(name = "user_id")
    )
    private Set<User> assignees = new HashSet<>();

    @ManyToOne(cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @JoinColumn(name = "creator_id", referencedColumnName = "id")
    private User creator;

    @Column(name = "creation_date", nullable = false)
    @CreatedDate
    private OffsetDateTime createdDate;

    @Column(name = "title", nullable = false)
    private String title;

    @Column(name = "description", nullable = false)
    private String description;

    @Column(name = "budget", nullable = false)
    private BigDecimal budget;

    @ManyToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "type_of_contribution_id", referencedColumnName = "id")
    private TaskType type;

    @Column(name = "contacts")
    private String contacts;

    @Column(name = "expected_delivery_time")
    private OffsetDateTime expectedDeliveryTime;

    @ManyToMany(cascade = {CascadeType.DETACH, CascadeType.MERGE, CascadeType.PERSIST, CascadeType.REFRESH})
    @JoinTable(
        name = "task_tags",
        joinColumns = {@JoinColumn(name = "task_id")},
        inverseJoinColumns = {@JoinColumn(name = "tag_id")}
    )
    private Set<Tag> tags = new HashSet<>();

    @Column(name = "update_date")
    @LastModifiedDate
    private OffsetDateTime updateDate;

    public Task(String title, String description, BigDecimal budget, String contacts, OffsetDateTime expectedDeliveryTime) {
        this.title = title;
        this.description = description;
        this.budget = budget;
        this.contacts = contacts;
        this.expectedDeliveryTime = expectedDeliveryTime;
        this.createdDate = OffsetDateTime.now();
        this.updateDate = createdDate;
    }
}
