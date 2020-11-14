	  $(document).ready(function(){
			$("#registerHere").validate({
				rules: {
						id_username:"required",
						id_email: {
									required: true,
									email: true
								  },
						id_password1: {
										required: true,
										minlength: 6
									  },
						id_password2: {
										required: true,
										equalTo: "#id_password1"
									  }
				},
				messages: {
							id_username: gettext("Enter your first and last name"),
							id_email: {
										required: gettext("Enter your email address"),
										email: gettext("Enter valid email address")
									  },
							id_password1: {
											required: gettext("Enter your password"),
											minlength: gettext("Password must be minimum 6 characters")
										  },
							id_password2: {
											required: gettext("Enter confirm password"),
											equalTo: gettext("Password and Confirm Password must match")
										  }
				},
				errorClass: "help-inline",
				errorElement: "span",
				highlight: function(element, errorClass, validClass) { 
					$(element).parents('.control-group').removeClass('success');
					$(element).parents('.control-group').addClass('error');
				},
				unhighlight: function(element, errorClass, validClass) {
					$(element).parents('.control-group').removeClass('error');
					$(element).parents('.control-group').addClass('success');
				}
			});
		});
