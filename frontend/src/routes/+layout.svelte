<script lang="ts">
	import Logo from '$lib/Logo.svelte';
	import '../app.css';
</script>

<aside class="sidebar justify-start">
	<section class="sidebar-title items-center px-4 pt-4">
		<div class="mr-4"><Logo /></div>

		<div class="flex flex-col">
			<span>Syncpad</span>
		</div>
	</section>
	<div class="divider"></div>
	<section class="h-fit min-h-[20rem] overflow-visible">
		<nav class="menu rounded-md">
			<section class="menu-section">
				<ul class="menu-items">
					<li class="menu-item">
						<i class="las la-th-large"></i>
						<span>Dashboard</span>
					</li>
				</ul>
			</section>
		</nav>
	</section>
	<section class="sidebar-footer h-full justify-end bg-gray-2 pt-2">
		<div class="divider my-0"></div>
		<div class="dropdown z-50 flex h-fit w-full cursor-pointer hover:bg-gray-4">
			<label class="whites mx-2 flex h-fit w-full cursor-pointer p-0 hover:bg-gray-4" tabindex="0">
				<div class="flex flex-row gap-4 p-6">
					<i class="las la-cog"></i>
					<div class="flex flex-col">
						<span>Settings</span>
					</div>
				</div>
			</label>
			<div class="dropdown-menu dropdown-menu-right-top ml-2">
				<a class="dropdown-item text-sm">Profile</a>
				<a tabindex="-1" class="dropdown-item text-sm">Account settings</a>
				<a tabindex="-1" class="dropdown-item text-sm">Change email</a>
				<a tabindex="-1" class="dropdown-item text-sm">Subscriptions</a>
				<a tabindex="-1" class="dropdown-item text-sm">Change password</a>
				<a tabindex="-1" class="dropdown-item text-sm">Refer a friend</a>
				<a tabindex="-1" class="dropdown-item text-sm">Settings</a>
			</div>
		</div>
	</section>
</aside>

<slot />
