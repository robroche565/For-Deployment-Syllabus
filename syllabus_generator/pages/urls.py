from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login', views.login_view, name='login'),
    path('signup', views.signup_view, name='signup'),
    path('logout', views.logout, name='logout'),
    path('userpage', views.userpage_view, name='userpage'),
    path('settings', views.settings_view, name='settings'),
    path('custom_password_change/', views.custom_password_change_view, name='custom_password_change'),
    path('forgot_password/', views.forgot_pass_view, name='forgot_password'),
    path('reset_password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    
    
    path('templates_list', views.templates_list, name='templates_list'),
    path('new_template', views.new_template, name='new_template'),
    path('edit_template/id=<int:id>/', views.edit_template, name="edit_template"),
    

    path('new_syllabus', views.new_syllabus, name='new_syllabus'),
    path('show_syllabus/first/<int:id>/', views.SyllabusView1.as_view(), name='show_syllabus_first'),
    path('show_syllabus/second/<int:id>/', views.SyllabusView2.as_view(), name='show_syllabus_second'),
    path('edit_syllabus/<int:id>/', views.edit_syllabus, name='edit_syllabus'),
    # path('create_new_syllabus/', views.create_new_syllabus, name='create_new_syllabus'),
    
    #ajax dont touch
    #ajax for References
    path('ajax/source-reference/add/', views.AddReference.as_view(), name='add_reference'),
    path('ajax/source-reference/update/', views.UpdateReference.as_view(), name='update_reference'),
    path('ajax/source-reference/delete/', views.DeleteReference.as_view(), name='delete_reference'),
    path('ajax/source-reference/remove-selected/', views.RemoveSelectedReferences.as_view(), name='remove_selected_references'),
    path('ajax/source-reference/regenerate/', views.RegenerateReferences.as_view(), name='regenerate_references'),
    
    #ajax for Topics
    path('ajax/topic/add/', views.AddTopic.as_view(), name='add_topic'),
    path('ajax/topic/update/', views.UpdateTopic.as_view(), name='update_topic'),
    path('ajax/topic/delete/', views.DeleteTopic.as_view(), name='delete_topic'),
    path('ajax/topic/remove-selected/', views.RemoveSelectedTopics.as_view(), name='remove_selected_topics'),
    path('ajax/source-topic/regenerate/', views.RegenerateTopics.as_view(), name='regenerate_topics'),
    
    #ajax for Course Learning Outcome
    path('ajax/course-learning-outcome/add/', views.AddCourseLearningOutcome.as_view(), name='add_course_learning_outcome'),
    path('ajax/course-learning-outcome/update/', views.UpdateCourseLearningOutcome.as_view(), name='update_course_learning_outcome'),
    path('ajax/course-learning-outcome/delete/', views.DeleteCourseLearningOutcome.as_view(), name='delete_course_learning_outcome'),
    path('ajax/course-learning-outcome/remove-selected/', views.RemoveSelectedCLOs.as_view(), name='remove_selected_clos'),
    path('ajax/course-learning-outcome/regenerate/', views.RegenerateCLO.as_view(), name='regenerate_clo'),
     
    path('process_and_redirect/<int:syllabus_ai_id>/',views.ProcessAndRedirectView.as_view(), name='process_and_redirect'),
    path('proceed_and_redirect/<int:syllabus_ai_id>/',views.ProceeedAndRedirectView.as_view(), name='proceed_and_redirect'),
    
    path('ajax/course_rubric/add/', views.AddCourseRubric.as_view(), name='add_course_rubric'),
    path('ajax/course_rubric/delete/', views.DeleteCourseRubric.as_view(), name='delete_course_rubric'),
    path('ajax/course_rubric/udpate/', views.UpdateCourseRubric.as_view(), name='update_course_rubric'),
    path('ajax/regenerate_course_rubric/', views.RegenerateCourseRubricView.as_view(), name='regenerate_course_rubric'),
    
    path('ajax/course_rubric_item/add/', views.AddCourseRubricItem.as_view(), name='add_course_rubric_item'),
    path('ajax/course_rubric_item/delete/', views.DeleteCourseRubricItem.as_view(), name='delete_course_rubric_item'),
    path('ajax/course_rubric_item/edit/', views.EditCourseRubricItem.as_view(), name='edit_course_rubric_item'),
    
    path('ajax/course_outline/add/', views.AddCourseOutlineView.as_view(), name='Add_CourseOutline'),
    path('ajax/course_outline/delete/', views.DeleteCourseOutline.as_view(), name='delete_course_outline'),
    path('ajax/course_outline/edit/', views.UpdateCourseOutline.as_view(), name='update_course_outline'),
    path('ajax/course_outline/regenerate', views.RegenerateCourseOutline.as_view(), name='regenerate_course_outline'),
    
    path('ajax/course_content/add', views.AddNewCourseContent.as_view(), name='add_course_content'),
    path('ajax/dslo/add', views.AddNewDSLO.as_view(), name='add_dslo'),
    path('ajax/oba/add', views.AddNewOBA.as_view(), name='add_oba'),
    path('ajax/eoo/add', views.AddNewEOO.as_view(), name='add_eoo'),
    path('ajax/values/add', views.AddNewValues.as_view(), name='add_values'),
    path('pdf/id=<int:id>/', views.pdf, name='pdf')
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)